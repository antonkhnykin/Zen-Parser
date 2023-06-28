import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import psycopg2


def parsing_zen() -> None:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver_certain = webdriver.Chrome(service=service)
    urls_alphabet = set()
    cnt = 0
    limit_texts = 10000

    conn = psycopg2.connect(dbname='', user='', password='', host='', port=5432)
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

    conn.close()


if __name__ == '__main__':
    parsing_zen()
