import logging
import requests
from bs4 import BeautifulSoup
from clean_encoding import clean
from check_internet import check_internet
from ChromeDrivers import ChromeDrivers
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.remote_connection import LOGGER



def scrape_poem(title, poet=""):
    base_url = "https://www.poetryfoundation.org"

    search_url = f"{base_url}/search?query={title}"
    data = requests.get(search_url)
    html = BeautifulSoup(data.text, "lxml")

    [h.extract() for h in html(['style', 'script'])]

    results = html.find('ul', class_="c-vList c-vList_bordered c-vList_bordered_anomaly").find_all('li')

    link = ""

    for result in results:
        text = result.text.lower()
        if poet == "":
            if title.lower() in text and 'poem' in text:
                link = result.find('a', href=True)['href']
                break
        else:
            if title.lower() in text and poet.lower() in text and 'poem' in text:
                link = result.find('a', href=True)['href']
                break

    if link != "":
        link = base_url + link
    else:
        message = f"Couldn't find '{title}'"
        if poet != "":
            message += f" by {poet}"
        raise Exception(message)

    # set log level for driver only to error
    LOGGER.setLevel(logging.ERROR)


    manager = ChromeDrivers()
    driver = manager.get_driver()


    driver.get(link)
    data = driver.page_source

    driver.quit()

    html = BeautifulSoup(data, "lxml")

    [h.extract() for h in html(['style', 'script'])]

    poem_html = html.find('article', class_="o-article").find('div', class_="c-feature")

    poem_title = poem_html.find('div', class_="c-feature-hd").getText().strip()
    poem_poet = poem_html.find('div', class_="c-feature-sub c-feature-sub_vast").\
        getText().replace("By", "").replace("by", "").strip()

    poem_title = poem_title.replace("Launch Audio in a New Window", "").strip()
    poem_poet = poem_poet.replace("Launch Audio in a New Window", "").strip()

    poem_body = poem_html.find('div', class_="c-feature-bd").getText().strip()

    poem_title = clean(poem_title)
    poem_poet = clean(poem_poet)
    poem_body = clean(poem_body)
    return poem_title, poem_poet, poem_body


if __name__ == "__main__":
    print(scrape_poem("Once more unto the breach", "William Shakespeare"))
