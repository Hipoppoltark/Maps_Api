import os
import sys

import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt

SCREEN_SIZE = [600, 450]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.setWindowTitle('Отображение карты')
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.getImage('0.002,0.002', "37.530887,55.703118")
        self.spn = 0.002
        self.coor = [37.530887, 55.703118]

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            try:
                self.spn *= 2
                self.getImage(str(self.spn) + ',' + str(self.spn), f"{str(self.coor[0])},{str(self.coor[1])}")
            except BaseException:
                self.spn = 0.002
                self.coor = [37.530887, 55.703118]
        elif event.key() == Qt.Key_PageDown:
            try:
                self.spn /= 2
                self.getImage(str(self.spn) + ',' + str(self.spn), f"{str(self.coor[0])},{str(self.coor[1])}")
            except BaseException:
                self.spn = 0.002
                self.coor = [37.530887, 55.703118]
        elif event.key() == Qt.Key_Left:
            try:
                self.coor[0] -= self.spn * 0.5
                self.getImage(str(self.spn) + ',' + str(self.spn), f"{str(self.coor[0])},{str(self.coor[1])}")
            except BaseException:
                self.spn = 0.002
                self.coor = [37.530887, 55.703118]
        elif event.key() == Qt.Key_Right:
            try:
                self.coor[0] += self.spn * 0.5
                self.getImage(str(self.spn) + ',' + str(self.spn), f"{str(self.coor[0])},{str(self.coor[1])}")
            except BaseException:
                self.spn = 0.002
                self.coor = [37.530887, 55.703118]
        elif event.key() == Qt.Key_Up:
            try:
                self.coor[1] += self.spn * 0.5
                self.getImage(str(self.spn) + ',' + str(self.spn), f"{str(self.coor[0])},{str(self.coor[1])}")
            except BaseException:
                self.spn = 0.002
                self.coor = [37.530887, 55.703118]
        elif event.key() == Qt.Key_Up:
            try:
                self.coor[1] -= self.spn * 0.5
                self.getImage(str(self.spn) + ',' + str(self.spn), f"{str(self.coor[0])},{str(self.coor[1])}")
            except BaseException:
                self.spn = 0.002
                self.coor = [37.530887, 55.703118]

    def getImage(self, spn, coor):
        params = {
            "ll": coor,
            "spn": spn,
            "l": "map"
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
        print(self.pixmap)


    def closeEvent(self, event):
        """При закрытии формы подчищаем за собой"""
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())
