import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5 import uic  # Импортируем uic
from PyQt5.QtWidgets import QApplication, QMainWindow


APIKEY = "40d1649f-0493-4b70-98ba-98533de7710b"


class ClickedLabel(QLabel):
    clicked = pyqtSignal()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.setFocus()
        # это дальность координат от центра карты. По идее должны работать как
        # (координата в окне - центр окна) * scr / ширина ил длина окна
        # но не работает
        if e.button() == Qt.LeftButton:
            x = (e.x() - self.frameGeometry().width() / 2) * 3.4912 * self.master.spn / (self.frameGeometry().width())
            y = (self.frameGeometry().height() / 2 - e.y()) * 1.35 * self.master.spn / (self.frameGeometry().height())
            self.master.reset()
            response = requests.get(
                'https://geocode-maps.yandex.ru/1.x',
                params={
                    'format': 'json',
                    'apikey': APIKEY,
                    'geocode': str(self.master.coor[0] + x) + ',' + str(self.master.coor[1] + y)
                },
            )
            if response:
                try:
                    json_response = response.json()
                    object = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
                    address = object['metaDataProperty']['GeocoderMetaData']['text']
                    coords = object['Point']['pos']
                    try:
                        self.master.postal_code = object['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
                    except Exception:
                        self.master.postal_code = 'Нет почтового индекса'
                    coor_request = ','.join(coords.split())
                    self.master.mark = str(self.master.coor[0] + x) + ',' + str(self.master.coor[1] + y) + \
                                       ',pm2dirm'
                    if self.master.check_index.isChecked():
                        self.master.adress.setPlainText(address + '\n' + f'Почтовый индекс: {self.master.postal_code}')
                    else:
                        self.master.adress.setPlainText(address)
                    self.master.getImage(str(self.master.spn) + ',' + str(self.master.spn),
                                         ','.join(map(str, self.master.coor)),
                                         str(self.master.coor[0] + x) + ',' + str(self.master.coor[1] + y) + ',pm2dirm')
                except Exception:
                    self.master.statusBar().showMessage('Нам не удалось найти такой объект')


class Example(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('maps_main.ui', self)
        self.setWindowTitle('Отображение карты')
        self.image = ClickedLabel(self)
        self.image.move(0, 100)
        self.image.resize(650, 450)
        self.image.master = self
        self.getImage('0.002,0.002', "37.530887,55.703118", '')
        self.spn = 0.002
        self.spn2 = self.spn * 0.75
        self.coor = [37.530887, 55.703118]
        self.mark = ''
        self.postal_code = ''
        self.btn_search.clicked.connect(self.new_request)
        self.image.clicked.connect(self.change_focus)
        self.btn_reset.clicked.connect(self.reset)
        self.radioButton.clicked.connect(self.call_func_get_image)
        self.radioButton_2.clicked.connect(self.call_func_get_image)
        self.radioButton_3.clicked.connect(self.call_func_get_image)
        self.check_index.clicked.connect(self.call_func_request)
        self.x, self.y = self.coor[0], self.coor[1]

    def call_func_request(self):
        self.new_request()

    def call_func_get_image(self):
        self.getImage(str(self.spn) + ',' + str(self.spn), f"{str(self.coor[0])},{str(self.coor[1])}",
                      self.mark)

    def reset(self):
        self.adress.setPlainText('')
        self.mark = ''
        self.line_search.setText('')
        self.getImage(str(self.spn) + ',' + str(self.spn), f"{str(self.coor[0])},{str(self.coor[1])}",
                      self.mark)

    def get_map_type(self):
        if self.radioButton.isChecked():
            return "map"
        elif self.radioButton_2.isChecked():
            return "sat"
        elif self.radioButton_3.isChecked():
            return "sat,skl"

    def change_focus(self):
        self.image.setFocus()

    def new_request(self, mousepressed=[]):
        self.image.setFocus()
        response = requests.get(
            'https://geocode-maps.yandex.ru/1.x',
            params={
                'format': 'json',
                'apikey': APIKEY,
                'geocode': self.line_search.text() if self.line_search.text() else self.mark[:len(self.mark) - 8]
            },
        )
        if response:
            try:
                json_response = response.json()
                object = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
                address = object['metaDataProperty']['GeocoderMetaData']['text']
                try:
                    self.postal_code = object['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']
                except Exception:
                    self.postal_code = 'Нет почтового индекса'
                coords = object['Point']['pos']
                self.coor = [float(i) for i in coords.split()]
                coor_request = ','.join(coords.split())
                self.mark = f'{coor_request},pm2dirm'
                if self.check_index.isChecked():
                    self.adress.setPlainText(address + '\n' + f'Почтовый индекс: {self.postal_code}')
                else:
                    self.adress.setPlainText(address)
                self.getImage(str(self.spn) + ',' + str(self.spn), coor_request, self.mark)
            except Exception:
                self.statusBar().showMessage('Нам не удалось найти такой объект')

    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_PageUp:
                self.spn *= 2
            elif event.key() == Qt.Key_PageDown:
                self.spn /= 2
            elif event.key() == Qt.Key_Left:
                self.coor[0] = (self.coor[0] - self.spn * 0.5 + 180) % 360 - 180
            elif event.key() == Qt.Key_Right:
                self.coor[0] = (self.coor[0] + self.spn * 0.5 + 180) % 360 - 180
            elif event.key() == Qt.Key_Up:
                self.coor[1] += (self.spn * 0.5 + 180) % 360 - 180
            elif event.key() == Qt.Key_Down:
                self.coor[1] -= (self.spn * 0.5 + 180) % 360 - 180
            self.getImage(str(self.spn) + ',' + str(self.spn), f"{str(self.coor[0])},{str(self.coor[1])}",
                          self.mark)
        except BaseException:
            self.spn = 0.002
            self.coor = [37.530887, 55.703118]

    def getImage(self, spn, coor, mark):
        params = {
            "ll": coor,
            "spn": spn,
            "l": self.get_map_type(),
            'size': '650,450',
            'pt': mark
        }
        map_request = "http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_request, params=params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        # Запишем полученное изображение в файл.
        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        try:
            self.image.destroy()
        except BaseException:
            pass
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)


    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())