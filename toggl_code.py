from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QApplication, QScrollArea,\
    QColorDialog, QErrorMessage, QGridLayout, QGraphicsDropShadowEffect
from PyQt5.QtCore import QTimer
import time, datetime
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import sqlite3

import sys


class Autorization(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('toggl_authorization.ui', self)
        self.setWindowTitle("Авторизация")
        self.logged_in = False

        self.log_in_button.clicked.connect(self.log_in)
        self.sign_up_button.clicked.connect(self.sign_up)
        self.next_button.clicked.connect(self.next_window)

    def next_window(self):
        if self.logged_in:
            self.error_message_label.setStyleSheet("color: rgb(127, 127, 127)")
            self.close()
            toggl.show()
        else:
            self.error_message_label.setText('Сначала войдите в аккаунт.')
            self.error_message_label.setStyleSheet("color: rgb(255, 0, 0)")

    def log_in(self):  # вход!!
        login_flag = 0
        password_flag = 0
        print('Происходит вход')
        user_login = self.login.text()
        user_password = self.password.text()

        if user_login == '':
            self.error_message_label.setText('Введите логин.')
            self.error_message_label.setStyleSheet("color: rgb(255, 0, 0)")
            return
        if user_password == '':
            self.error_message_label.setText('Введите пароль.')
            self.error_message_label.setStyleSheet("color: rgb(255, 0, 0)")
            return

        for login in cursor.execute("SELECT login FROM users"):
            if user_login != login[0]:
                print("Такого логина нет")
                self.error_message_label.setText('Такого логина не существует. Попробуйте снова.')
                self.error_message_label.setStyleSheet("color: rgb(255, 0, 0)")
                login_flag = 1
            else:
                print('Такой логин нашелся')
                self.error_message_label.setStyleSheet("color: rgb(127, 127, 127)")
                login_flag = 0
                break
        if login_flag == 1:
            return
        for login_password in cursor.execute("SELECT login, password FROM users"):
            if user_login == login_password[0] and user_password != login_password[1]:
                print("Неверный пароль")
                self.error_message_label.setText('Неверный пароль. Попробуйте снова.')
                self.error_message_label.setStyleSheet("color: rgb(255, 0, 0)")
                password_flag = 1
            elif user_login == login_password[0] and user_password == login_password[1]:
                print('Верный пароль')
                self.error_message_label.setText('Вы успешно вошли в аккаунт.')
                self.error_message_label.setStyleSheet("color: rgb(0, 255, 0)")
                password_flag = 0
                self.logged_in = True
                self.current_login = user_login
                self.current_password = user_password
                break
        if password_flag == 1:
            return

    def sign_up(self): # регистрация
        print("Происходит регистрация")
        user_login = self.login.text()
        user_password = self.password.text()
        data = ''  # видимо нельзя совать списки

        if len(self.login.text()) < 3:
            print('Короткий логин')
            self.error_message_label.setText('Логин слишком короткий. Попробуйте снова.')
            self.error_message_label.setStyleSheet("color: rgb(255, 0, 0)")
            return

        if len(self.password.text()) < 6:
            print('Короткий пароль')
            self.error_message_label.setText('Пароль слишком короткий. Попробуйте снова.')
            self.error_message_label.setStyleSheet("color: rgb(255, 0, 0)")
            return

        self.error_message_label.setStyleSheet("color: rgb(127, 127, 127)")
        cursor.execute(f"SELECT login FROM users WHERE login = '{user_login}'")

        if cursor.fetchone() is None:
            cursor.execute(f"INSERT INTO users VALUES (?, ?, ?)", (user_login, user_password, data))
            data_base.commit()
            print('Зарегистрировано')
            self.error_message_label.setText('Вы успешно зарегистрированы.')
            self.error_message_label.setStyleSheet("color: rgb(0, 255, 0)")
        else:
            print('Такая запись уже имеется')
            self.error_message_label.setText('Такой логин уже существует. Попробуйте снова.')
            self.error_message_label.setStyleSheet("color: rgb(255, 0, 0)")
            return


class InsightsWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('toggl_insights.ui', self)


class MyWidget(QMainWindow):    # надо сразу выводить список задач из базы данных
    def __init__(self):
        super().__init__()
        uic.loadUi('toggl_app.ui', self)
        self.setWindowTitle("Toggl")

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
        self.stop.move(790, 47)
        self.start.move(750, 39)
        self.select_color.move(640, 60)

        self.insights_button.clicked.connect(self.view_insights)

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

    def view_insights(self):
        self.date_list = []
        self.time_list = []
        if self.history_list == []:
            self.insights_window = InsightsWindow()
            self.insights_window.insights_label.setText('Нет данных для составления вашей статистики.')
        else:
            self.insights_window = pg.GraphicsWindow()
            self.insights_window.resize(800, 350)
            self.insights_window.setWindowTitle('Статистика')
            plt1 = self.insights_window.addPlot()
            for data_list in self.history_list: # надо создать словарь, тут херня
                if not data_list[0].text()[:5] in self.date_list:   # и вообще этот модуль стремный
                    self.date_list.append(data_list[0].text()[:5])
                self.time_list.append(data_list[-1].text())   # надо прибавлять часы и делать статистику по дням
                print(data_list[-1].text())
                print(data_list[0].text()[:5])
            x = self.date_list # список дней
            y = self.time_list # список часов

            plt1.plot(x, y, stepMode=True, fillLevel=0, filloutline=True, brush=(200, 0, 255, 150))
        self.insights_window.show()

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
    # сортировка по дате(?)
    # диаграмма продуктивности
    def newtask(self):
        if '00:00:00' == self.timelabel.text() or '' == self.task.text():
            return
        else:
            self.scrollAreaWidgetContents = QWidget()
            self.scrollAreaWidgetContents.setMinimumSize(900, 400)
            self.grid = QGridLayout(self.scrollAreaWidgetContents)
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
            self.start_time_label = QLabel(f'{self.start_time}:')
            self.start_time_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 16))
            self.start_time_label_font = self.start_time_label.font()
            self.start_time_label_font.setUnderline(True)
            self.start_time_label.setFont(self.start_time_label_font)
            self.task_label = QLabel(f"  {self.task.text()}         ")
            self.task_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 16))
            self.time_label = QLabel(time.strftime("%H:%M:%S", time.gmtime(self.time)))
            self.time_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 16))
            self.history_list.append(
                [self.start_time_label, self.task_label, self.tag_label, self.color_label, self.time_label])
            self.reversed_list = self.history_list[::-1]
            for line in self.reversed_list:
                for label in line:
                    self.grid.addWidget(label, self.reversed_list.index(line), line.index(label))
            self.task.setText('')
            self.tag.setText('')
            if not self.no_color.isChecked():
                self.no_color.toggle()
            self.selected_color.setStyleSheet("color: rgb(127, 127, 127)")
            self.scroll_area.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.scroll_area.setWidget(self.scrollAreaWidgetContents)
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
    data_base = sqlite3.connect('toggl_db.db')
    cursor = data_base.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        login TEXT,
        password TEXT,
        data LIST
    )""")
    data_base.commit()
    for value in cursor.execute("SELECT * FROM users"):
        print(value)

    app = QApplication([])
    authorization = Autorization()
    authorization.show()
    toggl = MyWidget()
    sys.exit(app.exec_())
