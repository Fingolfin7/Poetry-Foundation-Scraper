import logging
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import html
from clean_encoding import clean
from ChromeDrivers import ChromeDrivers
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re, sys


def scrape_poem(title, poet="", log_level=logging.ERROR):
    LOGGER.setLevel(log_level)
    logger = logging.getLogger(__name__)
    logHandler = logging.StreamHandler(sys.stdout)
    logHandler.setFormatter(logging.Formatter('%(filename)s:%(lineno)s - %(levelname)s - %(message)s'))
    logger.addHandler(logHandler)
    logger.setLevel(log_level)

    driver = ChromeDrivers().get_driver()

    base_url = "https://www.poetryfoundation.org"
    search_url = f"{base_url}/search?query={quote_plus(title)}"
    driver.get(search_url)

    # --- Step 1: Wait for Search Results & Extract Link, Title, Poet from Search Page ---
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'ais-Hits'))
        )
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.ais-Hits article[data-layout="Inline"]'))
        )
    except Exception as e:
        driver.quit()
        raise Exception(f"Timeout waiting for search results to load for '{title}': {e}")

    data = driver.page_source
    html_soup_search_results = BeautifulSoup(data, "lxml")

    [h.extract() for h in html_soup_search_results(['style', 'script'])]

    found_poem_link = ""

    search_results_container = html_soup_search_results.find('div', class_='ais-Hits')
    results_articles = []
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
        current_title_text = html.unescape(current_title_text_raw).lower()

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

        if poet == "":
            if title.lower() in current_title_text:
                found_poem_link = current_link_href
                title = html.unescape(current_title_text_raw)
                poet = html.unescape(poet_text_raw.replace("By", "").replace("by", "")).strip() if poet_span else ""
                break
        else:
            if title.lower() in current_title_text and poet.lower() in current_poet_from_search:
                found_poem_link = current_link_href
                title = html.unescape(current_title_text_raw)
                poet = html.unescape(poet_text_raw.replace("By", "").replace("by", "")).strip() if poet_span else ""
                break

    if found_poem_link and not found_poem_link.startswith(base_url):
        found_poem_link = base_url + found_poem_link
    elif not found_poem_link:
        message = f"Couldn't find '{title}'"
        if poet != "":
            message += f" by {poet}"
        raise Exception(message)

    # --- Step 2: Navigate to Poem Page and Extract Content ---
    driver.get(found_poem_link)
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'poem-body'))
        )
    except Exception as e:
        driver.quit()
        raise Exception(f"Timeout waiting for poem-body to load for '{title}': {e}")

    data = driver.page_source
    driver.quit()

    html_soup_poem_page = BeautifulSoup(data, "lxml")

    [s.extract() for s in html_soup_poem_page(['style', 'script'])]

    poem_title_extracted = ""

    poem_body_content_div = html_soup_poem_page.find('div', class_='poem-body')

    if not poem_body_content_div:
        raise Exception("Couldn't find the main 'poem-body' div.")

    poem_lines_extracted_list = []

    line_divs = poem_body_content_div.find_all('div', style=lambda s: s and 'text-indent' in s)
    if not line_divs:
        line_divs = poem_body_content_div.find_all('div')

    for line_div in line_divs:
        # remove annotation text
        for annotation_text_span in line_div.find_all('span', id=lambda x: x and x.startswith('annotation-') and x.endswith('-text')):
            annotation_text_span.extract()

        line_text = line_div.get_text(separator=" ", strip=True)  # Use separator=" " to handle potential mixed content

        if line_text:
            poem_lines_extracted_list.append(line_text)

    if not poem_lines_extracted_list:
        logger.log(logging.WARNING,
                   f"Warning: No poem body text found in expected locations within 'poem-body' div.")

    poem_body_extracted = "\n".join(poem_lines_extracted_list)

    # Extract Title by parent search
    poem_info_container = None

    # Start from the poem_body_content_div's immediate parent
    current_element_for_info = poem_body_content_div.parent

    # Traverse up the DOM tree from the poem body's parent
    # Look for a parent that contains any h1/h2/h3. We are trying to find a *general heading* now.
    # Limit the search depth.
    for _ in range(7):  # Increased search depth slightly from 5 to 7
        if current_element_for_info is None:
            break

        has_any_heading_candidate = current_element_for_info.find(['h1', 'h2', 'h3'])

        if has_any_heading_candidate:  # The first parent with any heading
            poem_info_container = current_element_for_info
            logger.log(logging.DEBUG,f"Poem info container (for title) identified. Tag: <{poem_info_container.name}>")
            break

        current_element_for_info = current_element_for_info.parent

    if not poem_info_container:
        logger.log(logging.WARNING,"Warning: Could not identify suitable poem info container (parent of poem-body). Falling back to general soup search for title.")
        poem_info_container = html_soup_poem_page  # Fallback if specific structure is not found


    # Try finding common heading tags first that contain the title string
    potential_title_elements = poem_info_container.find_all(['h1', 'h2', 'h3'])

    for elem in potential_title_elements:
        extracted_title_text_candidate = elem.get_text(separator=" ", strip=True)
        if title.lower() in extracted_title_text_candidate.lower() and extracted_title_text_candidate:
            poem_title_extracted = extracted_title_text_candidate
            break

    # Final fallback for title extraction (if not found in headings)
    if not poem_title_extracted:
        # Search all text nodes, checking if it starts with the title, and is reasonable length
        all_text_nodes_in_info_container = poem_info_container.find_all(string=True)  # string=True for deprecation fix


        for text_node in all_text_nodes_in_info_container:
            stripped_text = text_node.strip()
            # Check if the stripped text starts with the title and is not just a fragment of other content
            if stripped_text.lower().startswith(title.lower()) and \
                    (len(title) + 70) > len(stripped_text) > 0 and \
                    not text_node.find_parent('a'):  # Avoid picking up titles from links in navigation, etc.

                # Try to get the containing block element for the title for better context
                parent_block = text_node.find_parent(['h1', 'h2', 'h3', 'div', 'p'])
                if parent_block:
                    poem_title_extracted = parent_block.get_text(strip=True)
                    logger.log(logging.DEBUG,f"DEBUG: Title found in block parent: '{poem_title_extracted}'")
                    break
                else:  # If no block parent, just use the text node itself
                    poem_title_extracted = stripped_text
                    logger.log(logging.DEBUG,f"DEBUG: Title found directly in text node: '{poem_title_extracted}'")
                    break

    if poem_title_extracted:
        logger.log(logging.DEBUG,f"Extracted Poem Title: '{poem_title_extracted}'")
    else:
        logger.log(logging.DEBUG,"Poem Title not found on page. Using title from search result / input.")
        poem_title_extracted = title  # Fallback to input 'title' if not found on page


    poem_poet_final = poet
    logger.log(logging.DEBUG,f"Using Poet from input/search results: '{poem_poet_final}'")

    poem_title_final = clean(poem_title_extracted)
    poem_poet_final = clean(poem_poet_final)
    poem_body_final = clean(poem_body_extracted)

    poem_title_final = poem_title_final.replace("Launch Audio in a New Window", "").strip()
    poem_poet_final = poem_poet_final.replace("Launch Audio in a New Window", "").strip()

    return poem_title_final, poem_poet_final, poem_body_final

if __name__ == "__main__":
    from random import choice

    # searchables = [("Once more unto the breach", "William Shakespeare"),
    #                ("The Road Not Taken", "Robert Frost"),
    #                ("The Second Coming", "William Butler Yeats"),
    #                ("Do not go gentle into that good night", "Dylan Thomas"),
    #                ("Ozymandias", "Percy Bysshe Shelley"),
    #                ("If—", "Rudyard Kipling"),
    #                ("The Tyger", "William Blake"),
    #                ("Kubla Khan", "Samuel Taylor Coleridge"),
    #                ("Ode to a Nightingale", "John Keats"),
    #                ("She Walks in Beauty", "Lord Byron"),
    #                ("The Charge of the Light Brigade", "Alfred, Lord Tennyson"),
    #                ("To His Coy Mistress", "Andrew Marvell"),
    #                ("Sonnet 18", "William Shakespeare")]

    searchables = [("The Second Coming", "William Butler Yeats"),
                   ("Ozymandias", "Percy Bysshe Shelley")
                   ]

    random_pick = choice(searchables)
    title, poet = random_pick
    print(f"Searching for: {title} by {poet}")
    _, _, poem = scrape_poem(title, poet, log_level=logging.DEBUG)
    print(poem)
    # try:
    #     _, _, poem = scrape_poem(title, poet)
    #     print(poem)
    # except Exception as e:
    #     print(e)


