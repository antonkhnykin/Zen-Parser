from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMenu, QWidget, QMessageBox, QFileDialog, QColorDialog, \
    QDialog, QHBoxLayout, QVBoxLayout, QSlider, QLabel, QDesktopWidget, QHeaderView, QFrame, QDockWidget, \
    QMainWindow, QAbstractItemView, QComboBox, QScrollArea
from PyQt5.QtCore import QEvent, Qt

from bs4 import BeautifulSoup
from urllib.request import urlopen
import re

soup = BeautifulSoup(urlopen("https://dzen.ru/a/ZDZT3TKOTFKPrnGx"), 'html.parser')

text = soup.get_text()
start = re.escape(" | ")
end = re.escape("прочитали")

title = text[:text.find("|")].strip()
text = re.sub('%s(.*)%s' % ('', end), r' ', text).strip()
print(title)
print(text)
