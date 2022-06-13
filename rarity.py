import requests
import bs4
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import json
from concurrent.futures import ThreadPoolExecutor


def fetcher(limit, supply, slug):
    vol = int(supply) * int(limit) // 100
    pages = []
    count = 0
    links = []
    if vol <= 100:
        pages.append(vol)
    else:
        a, b = divmod(vol, 100)
        while True:
            if count < a:
                count += 1
                i = 100
                pages.append(i)
            else:
                pages.append(100)
                break
    print(pages)

    def get_links(collection, max_rank, page_num, page_lim):
        print(page_num, page_lim)
        options = Options()
        serv = Service("./chromedriver.exe")
        options.add_argument('headless')
        options.add_argument(
            f'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36')
        driver = webdriver.Chrome(options=options, service=serv)
        url = "https://api.traitsniper.com/api/projects/{}/nfts?page={}&min_price=&max_price=&sort_price=&sort_last_sale_timestamp=&sort_last_sale_price=&min_rank=&max_rank=&token_id=&token=&from_token_id=&to_token_id=&trait_values=&sort_delta_price=&unrevealed=false&limit={}&trait_count=true&trait_norm=true".format(collection, str(page_num), str(page_lim))
        print(url)
        driver.get(url)
        soup = bs4.BeautifulSoup
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(
            (By.XPATH, "//pre[@style='word-wrap: break-word; white-space: pre-wrap;']")))
        scrape = soup(driver.page_source, 'html.parser').text
        js = json.loads(scrape)
        for nft in js["nfts"]:
            if int(nft["rarity_rank"]) <= int(max_rank):
                print(nft["rarity_rank"], nft["opensea_url"])
                links.append(nft["opensea_url"])
    with ThreadPoolExecutor(max_workers=5) as executor:
        [executor.submit(get_links, slug, vol, index, page) for (index, page) in enumerate(pages)]
    print(links)
    print(len(links))
    file = open("{}.txt".format(slug), "a")
    for link in links:
        file.write(link + "\n")
    file.close()


percent = input("% of top rare items: ")
volume = input("Total supply of the collection ")
col = input("Collection slug: ")

fetcher(percent, volume, col)
