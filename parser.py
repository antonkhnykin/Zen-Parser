import sys

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import psycopg2
import pandas as pd


def parsing_zen() -> None:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver_certain = webdriver.Chrome(service=service)
    urls_alphabet = set()
    cnt = 0
    limit_texts = 10000

    conn = psycopg2.connect(dbname='', user='',
                            password='', host='localhost', port=5432)
    conn.autocommit = True
    cur = conn.cursor()

    # Loading the catalog
    URL = 'https://dzen.ru/media/zen/channels'
    driver.maximize_window()
    driver.get(URL)
    elements = driver.find_elements(By.CLASS_NAME, 'alphabet__item')
    for i in range(len(elements)):
        if elements[i].text in 'АБВГДЕЁЖЗИКЛМНОПРСТУФХЦЧШЩЮЯ':
            urls_alphabet.add(elements[i].get_attribute('href'))

    # Adding channels from letter
    for url in urls_alphabet:
        driver.get(url)
        if cnt > limit_texts:
            break

        while True:
            elements = driver.find_elements(By.CLASS_NAME, 'channel-item__link')
            for i in range(len(elements)):
                try:
                    driver_certain.get(elements[i].get_attribute('href'))
                    elements_channel = driver_certain.find_elements(By.CLASS_NAME, 'card-image-compact-view__clickable')

                    driver_certain.get(elements_channel[0].get_attribute('href'))
                    title = driver_certain.find_element(By.CLASS_NAME, 'article__title')
                    elements_block = driver_certain.find_elements(By.CLASS_NAME, 'article-render__block_unstyled')
                    text = ''
                    for element in elements_block:
                        if element.text.strip() != '':
                            text = text + ' ' + element.text.strip()
                            if len(text) > 1000:
                                cnt += 1
                                cur.execute("INSERT INTO texts_zen(source, text, title, suggestio, modus, status, channel) "
                                            "VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}')".format('', text.strip(),
                                                                                                       title.text, -10, -10, 0, elements[i].get_attribute('href')))
                                break
                except:
                    pass

            if cnt > limit_texts:
                break
            if driver.find_element('link text', 'Следующие 20').text == 'Следующие 20':
                driver.find_element('link text', 'Следующие 20').click()
            else:
                break

    # Adding links from channel
    # for url in urls_channels:
    #     driver.get(url)

        # SCROLL_PAUSE_TIME = 0.5
        # last_height = driver.execute_script("return document.body.scrollHeight")
        # while True:
        #     # Scroll down to bottom
        #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #     # Wait to load page
        #     time.sleep(SCROLL_PAUSE_TIME)
        #     # Calculate new scroll height and compare with last scroll height
        #     new_height = driver.execute_script("return document.body.scrollHeight")
        #     if new_height == last_height:
        #         break
        #     last_height = new_height
        #
        # elements = driver.find_elements(By.CLASS_NAME, 'card-image-compact-view__clickable')
        # for i in range(len(elements)):
        #     urls_full.add(elements[i].get_attribute('href'))
        #     break

    conn.close()


if __name__ == '__main__':
    parsing_zen()
