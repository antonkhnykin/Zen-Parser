from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMenu, QWidget, QMessageBox, QFileDialog, QColorDialog, \
    QDialog, QHBoxLayout, QVBoxLayout, QSlider, QLabel, QDesktopWidget, QHeaderView, QFrame, QDockWidget, \
    QMainWindow, QAbstractItemView, QComboBox, QScrollArea
from PyQt5.QtCore import QEvent, Qt

from urllib.request import urlopen
import re
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


class AppParser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Парсинг")
        self.setFixedWidth(600)
        self.setFixedHeight(400)
        self.show()

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.setCentralWidget(self.centralwidget)
        self.verticalLayout_main = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_main.setContentsMargins(0, 2, 0, 0)
        self.verticalLayout_main.setSpacing(0)
        self.horizontalLayout_main = QtWidgets.QHBoxLayout()
        self.horizontalLayout_main.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_main.setSpacing(0)
        self.horizontalLayout_bottom = QtWidgets.QHBoxLayout()
        self.horizontalLayout_bottom.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_bottom.setSpacing(0)
        self.verticalLayout_main.addLayout(self.horizontalLayout_main)
        self.verticalLayout_main.addLayout(self.horizontalLayout_bottom)

        self.tabs = QtWidgets.QTabWidget(self.centralwidget)
        self.tabs.setGeometry(QtCore.QRect(10, 10, 400, 200))
        self.tabs.setStyleSheet("background-color: rgb(252, 252, 252);")

        # tab for Zen
        self.tab_zen = QtWidgets.QWidget()
        self.tabs.addTab(self.tab_zen, "Парсинг Дзен")
        self.horizontalLayout_zen = QtWidgets.QHBoxLayout(self.tab_zen)
        self.horizontalLayout_zen.setContentsMargins(0, 0, 0, 0)
        self.text_zen = QtWidgets.QLabel(self.tab_zen)
        self.text_zen.setText("URL канала")
        self.text_zen.setGeometry(QtCore.QRect(10, 10, 100, 20))
        self.edit_url = QtWidgets.QLineEdit(self.tab_zen)
        self.edit_url.setGeometry(QtCore.QRect(10, 40, 300, 20))
        self.pushbutton_zen = QtWidgets.QPushButton(self.tab_zen)
        self.pushbutton_zen.setGeometry(QtCore.QRect(10, 70, 225, 25))
        self.pushbutton_zen.setText("Начать парсинг")
        self.pushbutton_zen.clicked.connect(self.button_parsing_zen)

        # tab for VK
        self.tab_vk = QtWidgets.QWidget()
        self.tabs.addTab(self.tab_vk, "Парсинг ВК")


    def button_parsing_zen(self) -> None:
        # conn = psycopg2.connect(dbname='suggestio', user='postgres',
        #                         password='qwerty', host='localhost', port=5432)
        # df = pd.read_sql_query("SELECT * from texts_zen", con=conn)
        # print(df['text'])
        # conn.close()
        # return

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        urls_alphabet = set()
        urls_channels = set()
        urls_full = set()

        # Loading the catalog
        URL = 'https://dzen.ru/media/zen/channels'
        driver.maximize_window()
        driver.get(URL)
        elements = driver.find_elements(By.CLASS_NAME, 'alphabet__item')
        for i in range(len(elements)):
            if elements[i].text in 'АБВГДЕЁЖЗИКЛМНОПРСТУФХЦЧШЩЮЯ':
                urls_alphabet.add(elements[i].get_attribute('href'))
        print('Количество буквоссылок - {}'.format(len(urls_alphabet)))
        print('---------------')

        # Adding channels from letter
        for url in urls_alphabet:
            driver.get(url)
            if len(urls_channels) > 60:
                break
            while True:
                elements = driver.find_elements(By.CLASS_NAME, 'channel-item__link')
                for i in range(len(elements)):
                    urls_channels.add(elements[i].get_attribute('href'))
                if len(urls_channels) > 60:
                    break
                print('Количество каналоссылок - {}'.format(len(urls_channels)))
                print('---------------')
                if driver.find_element('link text', 'Следующие 20').text == 'Следующие 20':
                    driver.find_element('link text', 'Следующие 20').click()
                else:
                    break

#        with open('result.txt', 'w', encoding='utf-8') as f:
#            for url in urls_channels:
#                f.write(url + '\n')

#        conn = psycopg2.connect(dbname='suggestio', user='postgres',
#                                password='qwerty', host='localhost', port=5432)
#        df = pd.read_sql_query("SELECT * from texts_zen", con=conn)
#        print(df['text'])
#        conn.close()

        # Adding links from channel
        for url in urls_channels:
            driver.get(url)

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

            try:
                elements = driver.find_elements(By.CLASS_NAME, 'card-image-compact-view__clickable')
                for i in range(len(elements)):
                    urls_full.add(elements[i].get_attribute('href'))
                    break
            except TimeoutException as _ex:
                print('ОШИБКА: проблемы со ссылками')
                return
        print('Количество ссылок - {}'.format(len(urls_full)))
        print('---------------')

        conn = psycopg2.connect(dbname='suggestio', user='postgres',
                                password='qwerty', host='localhost', port=5432)
        conn.autocommit = True
        cur = conn.cursor()

        # conn = psycopg2.connect(dbname='suggestio', user='postgres',
        #                         password='qwerty', host='localhost', port=5432)
        # df = pd.read_sql_query("SELECT * from texts_zen", con=conn)
        # print(df['text'])
        # conn.close()

        with open('result.txt', 'w', encoding='utf-8') as f:
            for url in urls_full:
                driver.get(url)
                try:
                    title = driver.find_element(By.CLASS_NAME, 'article__title')
                    elements = driver.find_elements(By.CLASS_NAME, 'article-render__block_unstyled')
                    text = ''
                    for element in elements:
                        if element.text.strip() != '':
                            text = text + ' ' + element.text.strip()
                            if len(text) > 1000:
                                f.write('ЗАГОЛОВОК: ' + title.text + '\n')
                                f.write(text.strip() + '\n\n\n')
                                cur.execute("INSERT INTO texts_zen(source, text, title, suggestio, modus, status) "
                                            "VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(url, text.strip(), title.text, -10, -10, 0))
                                break
                except TimeoutException as _ex:
                    print('ОШИБКА: проблемы, Хьюстон')

        conn.close()


# soup = BeautifulSoup(urlopen(url), 'html.parser')
# text = soup.get_text()
# start = re.escape(" | ")
# end = re.escape("Войти")
#
# title = text[:text.find("|")].strip()
# text = re.sub('%s(.*)%s' % ('', end), r' ', text)

app = QtWidgets.QApplication(sys.argv)
app.setStyle('windowsvista')
MainWindow = QtWidgets.QMainWindow()
ui = AppParser()
sys.exit(app.exec_())
