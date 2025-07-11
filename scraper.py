import logging
import requests
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import html
from clean_encoding import clean
from ChromeDrivers import ChromeDrivers
from selenium.webdriver.remote.remote_connection import LOGGER

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import re


def scrape_poem(title, poet=""):
    LOGGER.setLevel(logging.ERROR)
    driver = ChromeDrivers().get_driver()
    base_url = "https://www.poetryfoundation.org"
    search_url = f"{base_url}/search?query={quote_plus(title)}"
    driver.get(search_url)

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
    html_soup = BeautifulSoup(data, "lxml")

    [h.extract() for h in html_soup(['style', 'script'])]

    link = ""

    search_results_container = html_soup.find('div', class_='ais-Hits')
    results_articles = []
    if search_results_container:
        results_articles = search_results_container.find_all('article', attrs={"data-layout": "Inline"})
    else:
        results_articles = html_soup.find_all('article', attrs={"data-layout": "Inline"})

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
        current_poet_text = ""
        if poet_span:
            poet_text_raw = poet_span.get_text(strip=True)
            poet_match = re.search(r'(?i)By\s+(.*)', poet_text_raw)
            if poet_match:
                current_poet_text = html.unescape(poet_match.group(1)).lower().strip()
            else:
                current_poet_text = html.unescape(poet_text_raw).lower().strip()

        if poet == "":
            if title.lower() in current_title_text:
                link = current_link_href
                break
        else:
            if title.lower() in current_title_text and poet.lower() in current_poet_text:
                link = current_link_href
                break

    if link and not link.startswith(base_url):
        link = base_url + link
    elif not link:
        message = f"Couldn't find '{title}'"
        if poet != "":
            message += f" by {poet}"
        raise Exception(message)

    driver.get(link)
    # --- REVISED WAIT: Wait for the central poem-body div ---
    try:
        # This is the most reliable element for the actual poem text
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'poem-body'))
        )
    except Exception as e:
        driver.quit()
        raise Exception(f"Timeout waiting for poem-body to load for '{title}': {e}")

    data = driver.page_source
    driver.quit()

    html_soup = BeautifulSoup(data, "lxml")

    [h.extract() for h in html_soup(['style', 'script'])]

    print("\n--- Starting Poem Content Extraction ---")
    print(f"Current URL: {link}")

    poem_title = ""
    poem_poet = ""
    poem_body = ""

    # --- NEW: Find the poem_container based on its unique children ---
    poem_container = None

    # Iterate through all <div> and <article> tags, looking for one that *contains*
    # an <h1>/<h2> (title), a "By" span (poet), and the "poem-body" div.
    potential_wrappers = html_soup.find_all(['div', 'article'])

    print(f"Number of potential wrappers to check: {len(potential_wrappers)}")
    for i, wrapper in enumerate(potential_wrappers):
        # Must have a primary title within it
        has_title = wrapper.find(['h1', 'h2'])

        # Must have a poet's byline within it
        has_poet = wrapper.find('span', class_=lambda x: x and 'c-byline' in x) or \
                   re.search(r'(?i)By\s+([A-Za-z.\s\-]+)', wrapper.get_text()[:500])  # Look for "By" in first 500 chars

        # Must contain the specific poem body div
        has_poem_body_div = wrapper.find('div', class_='poem-body')

        # if i < 10: # Print only first few for brevity
        #     print(f"  Checking wrapper {i+1} (<{wrapper.name}>). Title: {bool(has_title)}, Poet: {bool(has_poet)}, PoemBodyDiv: {bool(has_poem_body_div)}")

        if has_title and has_poet and has_poem_body_div:
            poem_container = wrapper
            print(
                f"  Selected wrapper {i + 1} as poem_container: <{wrapper.name}> (Snippet: {wrapper.get_text(strip=True)[:100]}...)")
            break

    if not poem_container:
        raise Exception("Couldn't identify the main poem content container based on unique children.")
    else:
        print("--- Poem container identified. ---")
        # print(f"Poem container prettified (first 500 chars):\n{poem_container.prettify()[:500]}...")

    # --- Extracting Title within the identified poem_container ---
    title_element = poem_container.find(['h1', 'h2'])  # Find the most prominent heading
    if title_element:
        poem_title = title_element.get_text(separator=" ", strip=True)
        print(f"Extracted Poem Title: '{poem_title}'")
    else:
        print("Warning: No primary title element (h1/h2) found within poem_container.")

    # --- Extracting Poet within the identified poem_container ---
    poem_poet = ""
    # Try finding the specific byline span
    poet_span = poem_container.find('span', class_=lambda x: x and 'c-byline' in x)
    if poet_span:
        poet_link = poet_span.find('a', class_='c-byline_link')
        if poet_link:
            poem_poet = poet_link.get_text(strip=True)
            print(f"Extracted Poem Poet (from link): '{poem_poet}'")
        else:  # Fallback to span text if no link, remove "By" if present
            raw_poet_text = poet_span.get_text(strip=True)
            if raw_poet_text.lower().startswith('by '):
                poem_poet = raw_poet_text[3:].strip()
            else:
                poem_poet = raw_poet_text
            print(f"Extracted Poem Poet (from span): '{poem_poet}'")

    # Fallback to general regex search within poem_container if specific span not found
    if not poem_poet:
        match = re.search(r'(?i)By\s+([A-Za-z.\s\-]+)', poem_container.get_text())
        if match:
            poem_poet = match.group(1).strip()
            print(f"Extracted Poem Poet (regex fallback on container): '{poem_poet}'")
        else:
            print("Warning: No poet found via any method within poem_container.")

    # --- REVISED: Extract Body based on div.poem-body ---
    poem_lines_extracted = []

    # Directly find the div with class "poem-body" within the identified poem_container
    poem_body_container = poem_container.find('div', class_='poem-body')

    if poem_body_container:
        # Each line is in its own <div> (often with inline style) with a <span> inside it.
        # Target divs with style attribute and look for span or direct text.
        line_divs = poem_body_container.find_all('div', style=lambda s: s and 'text-indent' in s)

        if not line_divs:  # Fallback if `text-indent` style isn't always present for all lines
            line_divs = poem_body_container.find_all('div')  # Just get all divs if no style

        for line_div in line_divs:
            line_text = ""
            span_tag = line_div.find('span')
            if span_tag:
                line_text = span_tag.get_text(strip=True)
            else:
                # If no span, get text directly from line_div
                line_text = line_div.get_text(strip=True)

            if line_text:  # Ensure the line isn't empty
                poem_lines_extracted.append(line_text)
            # You might want to detect empty divs/lines for stanza breaks here,
            # but for now, just collecting non-empty lines.

    if not poem_lines_extracted:
        print("Warning: No poem body text found in expected locations (div.poem-body > div > span/text).")

    poem_body = "\n".join(poem_lines_extracted)  # Use single newline for lines within a stanza
    print(f"\n--- Extracted Poem Body (first 500 chars):\n{poem_body[:500]}...")
    print(f"Total Body Length: {len(poem_body)}")

    # Final cleaning (after initial extraction)
    poem_title = clean(poem_title)
    poem_poet = clean(poem_poet)
    poem_body = clean(poem_body)

    # These specific replacements might not be needed if extraction is clean
    poem_title = poem_title.replace("Launch Audio in a New Window", "").strip()
    poem_poet = poem_poet.replace("Launch Audio in a New Window", "").strip()

    return poem_title, poem_poet, poem_body


if __name__ == "__main__":
    from random import choice

    searchables = [("Once more unto the breach", "William Shakespeare"),
                   ("The Road Not Taken", "Robert Frost"),
                   ("The Second Coming", "William Butler Yeats"),
                   ("Do not go gentle into that good night", "Dylan Thomas"),
                   ("Ozymandias", "Percy Bysshe Shelley"),
                   ("If—", "Rudyard Kipling"),
                   ("The Tyger", "William Blake"),
                   ("Kubla Khan", "Samuel Taylor Coleridge"),
                   ("Ode to a Nightingale", "John Keats"),
                   ("She Walks in Beauty", "Lord Byron"),
                   ("The Charge of the Light Brigade", "Alfred, Lord Tennyson"),
                   ("To His Coy Mistress", "Andrew Marvell"),
                   ("Sonnet 18", "William Shakespeare")]

    # searchables = [("The Second Coming", "William Butler Yeats"),
    #                ("A Prayer for my daughter", "William Butler Yeats")
    #                ]

    random_pick = choice(searchables)
    title, poet = random_pick
    print(f"Searching for: {title} by {poet}")
    _, _, poem = scrape_poem(title, poet)
    print(poem)
    # try:
    #     _, _, poem = scrape_poem(title, poet)
    #     print(poem)
    # except Exception as e:
    #     print(e)


