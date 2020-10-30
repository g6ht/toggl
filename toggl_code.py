from PyQt5 import uic, QtGui, QtCore  # Импортируем uic
from PyQt5.QtWidgets import QMainWindow, QPushButton, QRadioButton, QWidget, QLabel, QApplication,\
    QLineEdit, QScrollArea, QButtonGroup, QColorDialog, QErrorMessage, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QTimer, QRect
import time


import sys

class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultra demo")
        uic.loadUi('toggl.ui', self)
        self.scrollArea = QScrollArea(self.centralwidget)
        self.scrollArea.setGeometry(QtCore.QRect(170, 190, 361, 261))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 359, 259))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        # self.scroll_area = QScrollArea(self)
        # self.scroll_area.resize(1005, 471)
        # self.scroll_area.move(26, 180)
        # self.scroll_area.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
        # self.vertical = QVBoxLayout()
        # self.w = QWidget()
        # self.w.setLayout(self.vertical)
        # self.scroll_area.setWidget(self.w)

        self.line = ''
        self.color = ''
        self.start_text = QLabel(self)
        self.start_text.setText('Тут пока ничего нет...')
        self.start_text.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 20))
        self.scroll_area.setWidget(self.start_text)
        self.task.move(25, 50)
        self.tag.move(474, 50)
        self.stop.move(790, 47)
        self.start.move(750, 39)
        self.radiocounter = 0

        self.no_color.toggle() # если кликнута убрать надпись внизу
        self.select_color.clicked.connect(self.color_selection)

#  Сделать сортировку по дате
        timeout = pyqtSignal()
        self.time = 0
        self.timeInterval = 1000  # По умолчанию секунды

        self.timerUp = QTimer()
        self.timerUp.setInterval(self.timeInterval)
        self.timerUp.timeout.connect(self.updateUptime)

        self.start.clicked.connect(self.timerUp.start)
        self.pause.clicked.connect(self.timerUp.stop)
        self.stop.clicked.connect(self.timerUp.stop)
        self.stop.clicked.connect(self.newtask)
        self.stop.clicked.connect(self.reset)

    def updateUptime(self):
        self.time += 1
        self.settimer(self.time)


    def settimer(self, int):
        self.time = int
        self.timelabel.setText(time.strftime('%H:%M:%S', time.gmtime(self.time)))

    def reset(self):
        self.time = 0
        self.settimer(self.time)

    def newtask(self): # очищение таск при выводе
        task_name = QLabel()
        task_name.setText(self.task.text())
        print('ok')
        self.scrollAreaWidgetContents().addWidget(task_name)
        print("ok2")
        # if self.no_color.isChecked():
        #     self.color = ''
        #     print('wtf')
        # if '00:00:00' == self.timelabel.text() or '' == self.task.text():
        #     return
        # elif '' != self.tag.text() and '' != self.color:
        #     self.name = QLabel(self)
        #     print('!= !=')
        #     self.current_line = self.adjust(self.task.text(), self.tag.text(),
        #                                     time.strftime("%H:%M:%S", time.gmtime(self.time)), self.color)
        #     self.line = self.current_line + self.line
        #     self.name.setText(self.line)
        #     self.name.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 14))
        # elif '' == self.tag.text() and '' != self.color:
        #     self.name = QLabel(self)
        #     print("== !=")
        #     self.current_line = self.adjust(self.task.text(), '    ',
        #                                     time.strftime("%H:%M:%S", time.gmtime(self.time)), self.color)
        #     self.line = self.current_line + self.line
        #     self.name.setText(self.line)
        #     self.name.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 14))
        #
        # elif '' != self.tag.text() and '' == self.color:
        #     self.name = QLabel(self)
        #     print("!= ==")
        #     self.current_line = self.adjust(self.task.text(), self.tag.text(),
        #                                     time.strftime("%H:%M:%S", time.gmtime(self.time)))
        #     self.line = self.current_line + self.line
        #     self.name.setText(self.line)
        #     self.name.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 14))
        # elif '' == self.tag.text() and '' == self.color:
        #     self.name = QLabel(self)
        #     print("== ==")
        #     self.current_line = self.adjust(self.task.text(), '    ',
        #                                     time.strftime("%H:%M:%S", time.gmtime(self.time)))
        #     self.line = self.current_line + self.line
        #     self.name.setText(self.line)
        #     self.name.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 14))

        self.scroll_area.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        # print(self.name)
        # self.scroll_area.setWidget(self.name)
        self.scroll_area.show()

    def color_selection(self):
        self.radiocounter += 1
        color = QColorDialog.getColor()
        try:
            self.color = color.name()
            print(self.color)
            self.selected_color.setStyleSheet(f"color: {color.name()}")
            if self.radiocounter == 1:
                self.no_color.toggle()
        except TypeError:
            self.error_dialog = QErrorMessage()
            self.error_dialog.showMessage('Произошла ошибка. Видимо, такого цвета не существует')
            self.error_dialog.show()

# какие-то траблы с установкой цвета, надо менять окно вывода и делать по новой

    def adjust(self, task, tag, time, color=''):
        if len(task) < 10:
            task = task + '\t \t \t \t \t'
        elif 10 <= len(task) < 20:
            task = task + '\t \t \t \t  '
        elif 20 <= len(task) <= 35:
            task = task + '\t \t'
        else:
            pass
        if len(tag) < 10:
            tag = tag + '\t \t \t \t'
        elif 10 <= len(tag) <= 20:
            tag = tag + '\t \t \t'
        else:
            pass
        return f'{task}{tag}{time} \n'
#         '''<font color="red">Это</font><br>
# <font color="green">Цветной</font><br>
# <font color="blue">Текст</font><br>'''


if __name__ == '__main__':
    app = QApplication([])
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())