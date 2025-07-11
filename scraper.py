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
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'poem-body'))
        )
    except Exception as e:
        driver.quit()
        raise Exception(f"Timeout waiting for poem-body to load for '{title}': {e}")

    data = driver.page_source
    driver.quit()

    html_soup = BeautifulSoup(data, "lxml")

    [s.extract() for s in html_soup(['style', 'script'])]

    print("\n--- Starting Poem Content Extraction ---")
    print(f"Current URL: {link}")

    poem_title = ""
    poem_poet = ""
    poem_body = ""

    # --- CORE LOGIC FOR POEM PAGE EXTRACTION ---

    # 1. Find the main poem body div (our reliable anchor)
    poem_body_content_div = html_soup.find('div', class_='poem-body')

    if not poem_body_content_div:
        raise Exception("Couldn't find the main 'poem-body' div.")

    print("--- 'poem-body' div identified. ---")

    # 2. Extract Body Text (this part is already working well)
    poem_lines_extracted = []

    line_divs = poem_body_content_div.find_all('div', style=lambda s: s and 'text-indent' in s)
    if not line_divs:
        line_divs = poem_body_content_div.find_all('div')

    for line_div in line_divs:
        line_text = ""
        span_tag = line_div.find('span')
        if span_tag:
            line_text = span_tag.get_text(strip=True)
        else:
            line_text = line_div.get_text(strip=True)

        if line_text:
            poem_lines_extracted.append(line_text)

    if not poem_lines_extracted:
        print("Warning: No poem body text found in expected locations within 'poem-body' div.")

    poem_body = "\n".join(poem_lines_extracted)
    print(f"\n--- Extracted Poem Body (first 500 chars):\n{poem_body[:500]}...")
    print(f"Total Body Length: {len(poem_body)}")

    # --- REVISED: Extract Title and Poet by traversing relative to poem_body_content_div ---

    # Try to find the parent div (c-feature-bd) first
    c_feature_bd = poem_body_content_div.find_parent('div', class_='c-feature-bd')

    # If c_feature_bd found, then its previous siblings should be poet and title containers
    if c_feature_bd:
        print("--- Found parent 'c-feature-bd'. Now looking for siblings. ---")
        # Look for previous siblings: c-feature-sub (poet) and c-feature-hd (title)

        # Find poet div first (c-feature-sub)
        poet_div = c_feature_bd.find_previous_sibling('div', class_='c-feature-sub')
        if poet_div:
            poet_span = poet_div.find('span', class_='c-byline')
            if poet_span:
                poet_link = poet_span.find('a', class_='c-byline_link')
                if poet_link:
                    poem_poet = poet_link.get_text(strip=True)
                    print(f"Extracted Poem Poet (from c-byline link): '{poem_poet}'")
                else:
                    raw_poet_text = poet_span.get_text(strip=True)
                    if raw_poet_text.lower().startswith('by '):
                        poem_poet = raw_poet_text[3:].strip()
                    else:
                        poem_poet = raw_poet_text
                    print(f"Extracted Poem Poet (from c-byline span): '{poem_poet}'")

        # Find title div next (c-feature-hd)
        title_div = c_feature_bd.find_previous_sibling('div', class_='c-feature-hd')
        if title_div:
            title_element = title_div.find('h1', class_='c-feature-title')
            if not title_element:  # Fallback to h2 if no h1
                title_element = title_div.find('h2',
                                               class_='c-feature-title')  # Assuming c-feature-title might apply to h2
            if not title_element:  # Fallback to generic h1/h2 if class not used
                title_element = title_div.find(['h1', 'h2'])

            if title_element:
                poem_title = title_element.get_text(separator=" ", strip=True)
                print(f"Extracted Poem Title: '{poem_title}'")
            else:
                print("Warning: No specific title element found within c-feature-hd.")
        else:
            print("Warning: No 'c-feature-hd' div found as previous sibling.")

    else:  # Fallback if 'c-feature-bd' structure isn't found (less specific search)
        print("Warning: 'c-feature-bd' not found as parent of 'poem-body'. Falling back to general search.")
        # Revert to a general search for title/poet anywhere in the document, but less precise.
        # This part will likely be messy or empty if the specific structure is the dominant one.
        title_element_fallback = html_soup.find(['h1', 'h2'])
        if title_element_fallback:
            poem_title = title_element_fallback.get_text(separator=" ", strip=True)
            print(f"Extracted Poem Title (fallback): '{poem_title}'")

        poet_span_fallback = html_soup.find('span', class_=lambda x: x and 'c-byline' in x)
        if poet_span_fallback:
            poem_poet = poet_span_fallback.get_text(strip=True).replace("By", "").strip()
            print(f"Extracted Poem Poet (fallback): '{poem_poet}'")
        else:  # Generic regex on entire soup for a last resort
            match = re.search(r'(?i)By\s+([A-Za-z.\s\-]+)', html_soup.get_text())
            if match:
                poem_poet = match.group(1).strip()
                print(f"Extracted Poem Poet (regex fallback on whole document): '{poem_poet}'")

    if not poem_title:
        print("Final Warning: Poem Title remains empty.")
    if not poem_poet:
        print("Final Warning: Poem Poet remains empty.")

    # Final cleaning
    poem_title = clean(poem_title)
    poem_poet = clean(poem_poet)
    poem_body = clean(poem_body)

    # These specific replacements should ideally no longer be needed with precise extraction
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


