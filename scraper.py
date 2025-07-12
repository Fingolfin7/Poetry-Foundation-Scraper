import logging
import  sys
import re
import html
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from clean_encoding import clean
from ChromeDrivers import ChromeDrivers

# Import Selenium's wait tools
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.remote_connection import LOGGER  # Still needed to control Selenium's logger


class PoetryScraper:
    BASE_URL = "https://www.poetryfoundation.org"

    def __init__(self, log_level=logging.ERROR):
        self.logger = logging.getLogger(__name__ + ".PoetryScraper")

        # Configure logger to output to console
        logHandler = logging.StreamHandler(sys.stdout)
        logHandler.setFormatter(logging.Formatter('%(filename)s:%(lineno)s - %(levelname)s - %(message)s'))
        self.logger.addHandler(logHandler)

        self.logger.setLevel(log_level)

        # Configure Selenium's internal logger
        LOGGER.setLevel(logging.ERROR)

        self.chrome_driver_manager = ChromeDrivers(log_level=log_level)  # Instantiate ChromeDrivers

    def scrape_poem(self, title: str, poet: str = "") -> tuple[str, str, str]:
        """
        Scrapes a poem from PoetryFoundation.org.

        Args:
            title (str): The title of the poem to search for.
            poet (str, optional): The name of the poet. Defaults to "".

        Returns:
            tuple[str, str, str]: A tuple containing (poem_title, poem_poet, poem_body).

        Raises:
            Exception: If the poem or search results cannot be found within the timeout.
        """
        driver = None  # Initialize driver to None
        try:
            driver = self.chrome_driver_manager.get_driver()
            title = clean(title)
            search_url = f"{self.BASE_URL}/search?query={quote_plus(title)}"
            driver.get(search_url)

            # --- Step 1: Wait for Search Results & Extract Link, Title, Poet from Search Page ---
            self.logger.debug(f"Searching for '{title}' by '{poet}' on {search_url}")
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'ais-Hits'))
                )
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.ais-Hits article[data-layout="Inline"]'))
                )
            except Exception as e:
                raise Exception(f"Timeout waiting for search results to load for '{title}': {e}")

            data = driver.page_source
            html_soup_search_results = BeautifulSoup(data, "lxml")

            # Remove script and style tags from search results page HTML
            [h.extract() for h in html_soup_search_results(['style', 'script'])]

            found_poem_link = ""

            # Use original title and poet as initial return values
            # These will be updated if a better version is found on the search page
            # and passed to the poem page for final extraction.
            poem_title_final = title
            poem_poet_final = poet

            search_results_container = html_soup_search_results.find('div', class_='ais-Hits')

            if search_results_container:
                results_articles = search_results_container.find_all('article', attrs={"data-layout": "Inline"})
            else:
                results_articles = html_soup_search_results.find_all('article', attrs={"data-layout": "Inline"})

            if not results_articles:
                raise Exception(f"Couldn't find any search results (articles) for '{title}' after waiting.")

            for article_result in results_articles:
                type_span = article_result.find('span', class_=lambda x: x and 'type-iota' in x)
                if not type_span or "poem" not in type_span.get_text(strip=True).lower():
                    continue

                title_h3 = article_result.find('h3')
                if not title_h3:
                    continue

                current_link_element = title_h3.find('a', href=True)
                if not current_link_element:
                    continue

                current_title_text_raw = current_link_element.get_text(separator=" ", strip=True)
                current_title_text_lower = html.unescape(current_title_text_raw).lower()  # Use lower for comparison

                current_link_href = current_link_element['href']

                poet_span = article_result.find('span', class_=lambda x: x and 'type-kappa' in x)
                current_poet_from_search = ""
                if poet_span:
                    poet_text_raw = poet_span.get_text(strip=True)
                    poet_match = re.search(r'(?i)By\s+(.*)', poet_text_raw)
                    if poet_match:
                        current_poet_from_search = html.unescape(poet_match.group(1)).lower().strip()
                    else:
                        current_poet_from_search = html.unescape(poet_text_raw).lower().strip()

                # Decision logic for choosing the poem link
                if poet == "":  # If no specific poet provided, just match by title
                    if title.lower() in current_title_text_lower:
                        found_poem_link = current_link_href
                        poem_title_final = html.unescape(
                            current_title_text_raw).strip()  # Use cleaned title from search result
                        poem_poet_final = html.unescape(
                            poet_text_raw.replace("By", "").replace("by", "")).strip() if poet_span else ""
                        self.logger.debug(
                            f"Found match by title: '{poem_title_final}' by '{poem_poet_final}'. Link: {found_poem_link}")
                        break
                else:  # If poet provided, match both title and poet
                    if title.lower() in current_title_text_lower and poet.lower() in current_poet_from_search:
                        found_poem_link = current_link_href
                        poem_title_final = html.unescape(
                            current_title_text_raw).strip()  # Use cleaned title from search result
                        # Use regex to remove 'By ' (case-insensitive) only at the beginning
                        cleaned_poet_text = re.sub(r'^By\s+', '', poet_text_raw, flags=re.IGNORECASE).strip()
                        poem_poet_final = html.unescape(
                            cleaned_poet_text) if poet_span else ""  # No .strip() after unescape, as it's already stripped from regex
                        self.logger.debug(
                            f"Found exact match: '{poem_title_final}' by '{poem_poet_final}'. Link: {found_poem_link}")
                        break

            if not found_poem_link:  # Ensure link is found inside the loop
                self.logger.warning(f"No specific poem link found matching '{title}' by '{poet}' among search results.")

            if found_poem_link and not found_poem_link.startswith(self.BASE_URL):
                found_poem_link = self.BASE_URL + found_poem_link
            elif not found_poem_link:
                message = f"Couldn't find a matching poem link for '{title}'"
                if poet != "":
                    message += f" by {poet}"
                raise Exception(message)

            # Step 2: Get Poem Text from Found Poem Link
            self.logger.debug(f"Navigating to poem page: {found_poem_link}")
            driver.get(found_poem_link)
            try:
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'poem-body'))
                )
            except Exception as e:
                raise Exception(f"Timeout waiting for poem-body to load for '{poem_title_final}': {e}")

            data = driver.page_source # Driver is quit in the finally block

            html_soup_poem_page = BeautifulSoup(data, "lxml")
            [s.extract() for s in html_soup_poem_page(['style', 'script'])]

            poem_body_extracted = ""

            # Find the main poem body div
            poem_body_content_div = html_soup_poem_page.find('div', class_='poem-body')

            if not poem_body_content_div:
                raise Exception("Couldn't find the main 'poem-body' div on poem page.")

            self.logger.debug("'poem-body' div found.")

            # Extract Text
            poem_lines_extracted_list = []

            line_divs = poem_body_content_div.find_all('div', style=lambda s: s and 'text-indent' in s)
            if not line_divs:
                line_divs = poem_body_content_div.find_all('div')  # Fallback if style isn't consistent

            for line_div in line_divs:
                # Remove annotation spans and their text counterparts
                for annotation_text_span in line_div.find_all('span', id=lambda x: x and x.startswith(
                        'annotation-') and x.endswith('-text')):
                    annotation_text_span.extract()

                line_text = line_div.get_text(separator=" ", strip=True)

                if line_text:
                    poem_lines_extracted_list.append(line_text)

                # Check if this line_div is an empty break marker div: <div><br></div>
                # This should be the most reliable way to detect explicit stanza breaks.
                if not line_text and line_div.find('br'):
                    if poem_lines_extracted_list and poem_lines_extracted_list[-1] != "":
                        poem_lines_extracted_list.append("") # will be joined with \n later

            if not poem_lines_extracted_list:
                self.logger.warning("No poem body text found in expected locations within 'poem-body' div.")

            poem_body_extracted = "\n".join(poem_lines_extracted_list)

            # grab title by parent search
            poem_title_from_page = ""  # Use a different variable name here

            poem_info_container = None
            current_element_for_info = poem_body_content_div.parent

            for _ in range(7):
                if current_element_for_info is None:
                    break

                has_any_heading_candidate = current_element_for_info.find(['h1', 'h2', 'h3'])

                if has_any_heading_candidate:
                    poem_info_container = current_element_for_info
                    self.logger.debug(
                        f"Poem info container (for title) identified. Tag: <{poem_info_container.name}>")
                    break

                current_element_for_info = current_element_for_info.parent

            if not poem_info_container:
                self.logger.warning(
                    "Could not identify suitable poem info container (parent of poem-body). Falling back to general soup search for title.")
                poem_info_container = html_soup_poem_page

            potential_title_elements = poem_info_container.find_all(['h1', 'h2', 'h3'])

            for elem in potential_title_elements:
                extracted_title_text_candidate = elem.get_text(separator=" ", strip=True)
                if poem_title_final.lower() in extracted_title_text_candidate.lower() and extracted_title_text_candidate:
                    poem_title_from_page = extracted_title_text_candidate
                    break

            if not poem_title_from_page:
                all_text_nodes_in_info_container = poem_info_container.find_all(string=True)

                for text_node in all_text_nodes_in_info_container:
                    stripped_text = text_node.strip()
                    if stripped_text.lower().startswith(poem_title_final.lower()) and \
                            (len(poem_title_final) + 70) > len(stripped_text) > 0 and \
                            not text_node.find_parent('a'):

                        parent_block = text_node.find_parent(['h1', 'h2', 'h3', 'div', 'p'])
                        if parent_block:
                            poem_title_from_page = parent_block.get_text(strip=True)
                            self.logger.debug(f"Title found in block parent (fallback): '{poem_title_from_page}'")
                            break
                        else:
                            poem_title_from_page = stripped_text
                            self.logger.debug(f"Title found directly in text node (fallback): '{poem_title_from_page}'")
                            break

            if poem_title_from_page:
                self.logger.debug(f"Extracted Poem Title from page: '{poem_title_from_page}'")
                poem_title_final = poem_title_from_page  # Update final title with page's version if found
            else:
                self.logger.debug("Poem Title not found on page. Using title from search result / input.")
                # poem_title_final already holds the value from the search result or initial input

            self.logger.debug(f"Final Poem Title: '{poem_title_final}'")
            self.logger.debug(f"Final Poet: '{poem_poet_final}'")

            # Cleaning
            poem_title_final = clean(poem_title_final)
            poem_poet_final = clean(poem_poet_final)
            poem_body_final = clean(poem_body_extracted)

            poem_title_final = poem_title_final.replace("Launch Audio in a New Window", "").strip()
            poem_poet_final = poem_poet_final.replace("Launch Audio in a New Window", "").strip()

            return poem_title_final, poem_poet_final, poem_body_final

        finally:  # Ensure driver is closed even if an error occurs
            if driver:
                driver.quit()



if __name__ == "__main__":
    from random import choice
    from ColourText import format_text

    scraper_instance = PoetryScraper(log_level=logging.DEBUG)
    searchables = [
        # ("Once more unto the breach", "William Shakespeare"),
        # ("The Road Not Taken", "Robert Frost"),
        # ("The Second Coming", "William Butler Yeats"),
        # ("Do not go gentle into that good night", "Dylan Thomas"),
        # ("Ozymandias", "Percy Bysshe Shelley"),
        # ("If", "Rudyard Kipling"),
        # ("The Tyger", "William Blake"),
        # ("Kubla Khan", "Samuel Taylor Coleridge"),
        # ("Ode to a Nightingale", "John Keats"),
        ("She Walks in Beauty", "Lord Byron"),
        # ("The Charge of the Light Brigade", "Alfred, Lord Tennyson"),
        # ("To His Coy Mistress", "Andrew Marvell"),
        # ("Sonnet 18", "William Shakespeare"),
        # ("Stopping by Woods on a Snowy Evening", "Robert Frost"),
        # ("Still I Rise", "Maya Angelou"),
    ]

    title, poet = choice(searchables)
    print(f"{format_text(f'[bright yellow]Searching for: {title} by {poet}[reset]')}")
    try:
        poem_title, poem_poet, poem_body = scraper_instance.scrape_poem(title, poet)

        print(f"{format_text(f'[green]Found {poem_title} by {poem_poet}![reset]')}")
        print(poem_body)
        print(f"{format_text(f'[cyan]-------------------------------------------[reset]')}")

    except Exception as e:
        print(f"{format_text(f'[bright red]Error: {e}[reset]\n')}")
