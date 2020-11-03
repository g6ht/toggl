from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QApplication, QScrollArea,\
    QColorDialog, QErrorMessage, QGridLayout, QGraphicsDropShadowEffect
from PyQt5.QtCore import QTimer
import time, datetime

import sys


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Toggl")
        uic.loadUi('toggl_app.ui', self)
        self.grid = QGridLayout()

        self.history_list = []

        self.scroll_area = QScrollArea(self)
        self.scroll_area.resize(1005, 471)
        self.scroll_area.move(26, 180)
        self.scroll_area.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)

        self.color = ''
        self.start_text = QLabel(self)
        self.start_text.setText('Тут пока ничего нет...')
        self.start_text.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 20))
        self.scroll_area.setWidget(self.start_text)
        self.task.move(25, 50)
        self.tag.move(474, 50)
        self.stop.move(790, 47)
        self.start.move(750, 39)

        self.no_color.toggle()
        self.no_color.clicked.connect(self.no_color_clicked)
        self.select_color.clicked.connect(self.color_selection)

        self.time = 0
        self.timeInterval = 1000

        self.timerUp = QTimer()
        self.timerUp.setInterval(self.timeInterval)
        self.timerUp.timeout.connect(self.updateUptime)

        self.start.clicked.connect(self.timerUp.start)
        self.start.clicked.connect(self.current_time)
        self.pause.clicked.connect(self.timerUp.stop)
        self.stop.clicked.connect(self.timerUp.stop)
        self.stop.clicked.connect(self.newtask)
        self.stop.clicked.connect(self.reset)

    def current_time(self):
        if '' == self.task.text():
            self.error_dialog = QErrorMessage()
            self.error_dialog.showMessage('Вам нужно обязательно ввести название задачи.')
            self.error_dialog.show()
            self.timerUp.stop()
            self.reset()
            return
        else:
            self.start_time = datetime.datetime.now()
            self.start_time = self.start_time.strftime("%d-%m-%Y %H:%M")

    def updateUptime(self):
        self.time += 1
        self.settimer(self.time)

    def settimer(self, int):
        self.time = int
        self.timelabel.setText(time.strftime('%H:%M:%S', time.gmtime(self.time)))

    def reset(self):
        self.time = 0
        self.settimer(self.time)

    # не скроллится
    def newtask(self):
        if '00:00:00' == self.timelabel.text() or '' == self.task.text():
            return
        else:
            if self.no_color.isChecked():
                self.color_label = QLabel('○')
                self.color_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 30))
            else:
                self.color_label = QLabel(f'<h1 style="color: {self.color};">●')
                self.color_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 15))
                self.shadow = QGraphicsDropShadowEffect(self, blurRadius=5.0,
                                                    color=QtGui.QColor("#000000"), offset=QtCore.QPointF(0.0, 0.0))
                self.color_label.setGraphicsEffect(self.shadow)
            if '' == self.tag.text():
                self.tag_label = QLabel(self.tag.text())
            else:
                self.tag_label = QLabel(f"#{self.tag.text()}")
                self.tag_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 16))
                self.tag_label_font = self.tag_label.font()
                self.tag_label_font.setItalic(True)
                self.tag_label.setFont(self.tag_label_font)
            self.out_widget = QWidget(self)
            self.out_widget.setFixedHeight(400)
            self.out_widget.setFixedWidth(900)
            self.out_widget.setLayout(self.grid)
            self.start_time_label = QLabel(f'{self.start_time}:')
            self.start_time_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 16))
            self.start_time_label_font = self.start_time_label.font()
            self.start_time_label_font.setUnderline(True)
            self.start_time_label.setFont(self.start_time_label_font)
            self.task_label = QLabel(f"  {self.task.text()}")
            self.task_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 16))
            self.time_label = QLabel(time.strftime("%H:%M:%S", time.gmtime(self.time)))
            self.time_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 16))
            self.history_list.append(
                [self.start_time_label, self.task_label, self.tag_label, self.color_label, self.time_label])
            self.reversed_list = self.history_list[::-1]
            for line in self.reversed_list:
                print(line)
                for label in line:
                    print(label)
                    print(self.reversed_list.index(line))
                    print(line.index(label))
                    self.grid.addWidget(label, self.reversed_list.index(line), line.index(label))

            self.scroll_area.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.task.setText('')
            self.tag.setText('')
            if not self.no_color.isChecked():
                self.no_color.toggle()
            self.selected_color.setStyleSheet("color: rgb(127, 127, 127)")
            self.scroll_area.setWidget(self.out_widget)
            self.scroll_area.show()

    def no_color_clicked(self):
        self.selected_color.setStyleSheet("color: rgb(127, 127, 127)")

    def color_selection(self):
        color = QColorDialog.getColor()
        try:
            self.color = color.name()
            self.selected_color.setStyleSheet(f"color: {color.name()}")
            if self.no_color.isChecked():
                self.no_color.toggle()
        except TypeError:
            self.error_dialog = QErrorMessage()
            self.error_dialog.showMessage('Произошла ошибка. Видимо, такого цвета не существует')
            self.error_dialog.show()


if __name__ == '__main__':
    app = QApplication([])
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
