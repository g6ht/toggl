from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QApplication, QScrollArea, \
    QColorDialog, QErrorMessage, QGridLayout, QGraphicsDropShadowEffect, QLineEdit
from PyQt5.QtCore import QTimer
import time, datetime
from pyqtgraph.Qt import QtCore, QtGui
import sqlite3

import sys


class Authorization(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('toggl_authorization.ui', self)
        self.setWindowTitle("Авторизация")
        self.logged_in = False
        self.setFixedSize(476, 314)

        self.log_in_button.clicked.connect(self.log_in)
        self.sign_up_button.clicked.connect(self.sign_up)
        self.next_button.clicked.connect(self.next_window)
        self.eye_button.clicked.connect(self.eye)

    def eye(self):
        if self.eye_button.isChecked():
            self.eye_button.setStyleSheet("background-color: rgb(195, 195, 195)")
            self.password.setEchoMode(QLineEdit.Normal)
        else:
            self.eye_button.setStyleSheet("background-color: rgb(127, 127, 127)")
            self.password.setEchoMode(QLineEdit.Password)

    def next_window(self):
        if self.logged_in:
            self.error_message_label.setStyleSheet("color: rgb(127, 127, 127)")
            self.close()
            toggl.show()
            toggl.start_func()
        else:
            self.error_message_label.setText('Сначала войдите в аккаунт.')
            self.error_message_label.setStyleSheet("color: rgb(255, 0, 0)")

    def log_in(self):  # вход
        password_flag = 0
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

        logins = [login[0] for login in cursor.execute("SELECT login FROM users")]
        if user_login not in logins:
            self.error_message_label.setText('Такого логина не существует. Попробуйте снова.')
            self.error_message_label.setStyleSheet("color: rgb(255, 0, 0)")
            return
        else:
            self.error_message_label.setStyleSheet("color: rgb(127, 127, 127)")
            for login_password in cursor.execute("SELECT login, password FROM users"):
                if user_login == login_password[0] and user_password != login_password[1]:
                    self.error_message_label.setText('Неверный пароль. Попробуйте снова.')
                    self.error_message_label.setStyleSheet("color: rgb(255, 0, 0)")
                    password_flag = 1
                elif user_login == login_password[0] and user_password == login_password[1]:
                    self.error_message_label.setText('Вы успешно вошли в аккаунт.')
                    self.error_message_label.setStyleSheet("color: rgb(0, 255, 0)")
                    password_flag = 0
                    self.logged_in = True
                    global current_login
                    current_login = user_login
                    break
            if password_flag == 1:
                return

    def sign_up(self):  # регистрация
        user_login = self.login.text()
        user_password = self.password.text()
        data = ''

        if len(self.login.text()) < 3:
            self.error_message_label.setText('Логин слишком короткий. Попробуйте снова.')
            self.error_message_label.setStyleSheet("color: rgb(255, 0, 0)")
            return

        if len(self.password.text()) < 6:
            self.error_message_label.setText('Пароль слишком короткий. Попробуйте снова.')
            self.error_message_label.setStyleSheet("color: rgb(255, 0, 0)")
            return

        self.error_message_label.setStyleSheet("color: rgb(127, 127, 127)")
        cursor.execute(f"SELECT login FROM users WHERE login = '{user_login}'")

        if cursor.fetchone() is None:
            cursor.execute(f"INSERT INTO users VALUES (?, ?, ?)", (user_login, user_password, data))
            data_base.commit()
            self.error_message_label.setText('Вы успешно зарегистрированы.')
            self.error_message_label.setStyleSheet("color: rgb(0, 255, 0)")
        else:
            self.error_message_label.setText('Такой логин уже существует. Попробуйте снова.')
            self.error_message_label.setStyleSheet("color: rgb(255, 0, 0)")
            return


class InsightsWindow(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('toggl_insights.ui', self)
        self.date_list = {}
        self.list_of_values = []
        cursor.execute(f"SELECT data FROM users WHERE login = '{current_login}'")
        data = f"{cursor.fetchone()[0]}"
        for line in data.split('\n'):
            if len(line) == 0:
                continue
            value = line.split("|")[0][:10]
            time_value = line.split("|")[-1].strip()
            if value not in self.date_list.keys():
                self.date_list[value] = f'{time_value}'
            else:
                previous_time_value = self.date_list[value]
                previous_hours_value = int(previous_time_value[:2])
                hours_value = int(time_value[:2])
                previous_minutes_value = int(previous_time_value[3:5])
                minutes_value = int(time_value[3:5])
                previous_seconds_value = int(previous_time_value[6:])
                seconds_value = int(time_value[6:])
                hours_value = str(hours_value + previous_hours_value)
                minutes_value = str(minutes_value + previous_minutes_value)
                seconds_value = str(seconds_value + previous_seconds_value)
                if int(seconds_value) > 59:
                    minutes_value = str(int(minutes_value) + 1)
                    seconds_value = '00'
                if int(minutes_value) > 59:
                    hours_value = str(int(hours_value) + 1)
                    minutes_value = '00'
                if len(hours_value) == 1:
                    hours_value = f'0{hours_value}'
                if len(minutes_value) == 1:
                    minutes_value = f'0{minutes_value}'
                if len(seconds_value) == 1:
                    seconds_value = f'0{seconds_value}'
                time_value = f'{hours_value}:{minutes_value}:{seconds_value}'
                self.date_list[value] = f'{time_value}'

        if not toggl.history_list:
            self.insights_label.setText('Нет данных для составления вашей статистики.')
            self.insights_label.move(10, 150)
            self.insights_label_2.setStyleSheet("color: rgb(195, 195, 195)")
            self.insights_label_3.setStyleSheet("color: rgb(195, 195, 195)")
        else:
            self.insights_label.setText('Ваша статистика:')
            self.insights_label.move(10, 10)
            self.insights_label_2.setStyleSheet("color: rgb(0, 0, 0)")
            self.insights_label_3.setStyleSheet("color: rgb(0, 0, 0)")
            self.insights_scroll_area = QScrollArea(self)
            self.insights_scroll_area.resize(530, 310)
            self.insights_scroll_area.move(20, 75)
            self.scrollAreaWidgetContents1 = QWidget()
            self.scrollAreaWidgetContents1.setMinimumSize(510, 280)
            self.insights_grid = QGridLayout(self.scrollAreaWidgetContents1)
            n = 0
            for dates, times in self.date_list.items():
                date_label = QLabel(dates)
                date_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 15))
                time_label = QLabel(times)
                time_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 15))
                self.insights_grid.addWidget(date_label, n, 0)
                self.insights_grid.addWidget(time_label, n, 1)
                n += 1
            self.insights_scroll_area.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.insights_scroll_area.setWidget(self.scrollAreaWidgetContents1)
            self.insights_scroll_area.show()


class MyWidget(QMainWindow):  # добавить инглиш
    def __init__(self):
        super().__init__()
        uic.loadUi('toggl_app.ui', self)
        self.setWindowTitle("Toggl")
        self.setFixedSize(1062, 676)

        self.color = ''
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

    def start_func(self):
        cursor.execute(f"SELECT data FROM users WHERE login = '{current_login}'")
        data = f"{cursor.fetchone()[0]}"
        if data == '':
            self.history_list = []
            self.scroll_area = QScrollArea(self)
            self.scroll_area.resize(1005, 471)
            self.scroll_area.move(26, 180)
            self.scroll_area.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
            self.start_text = QLabel(self)
            self.start_text.setText('Тут пока ничего нет...')
            self.start_text.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 20))
            self.scroll_area.setWidget(self.start_text)
            self.scroll_area.show()
        else:
            self.history_list = []
            for task in data.split('\n'):
                labels = []
                if len(task) == 0:
                    continue
                for label in task.split('|'):
                    out_label = QLabel(label.strip())
                    if label == task.split('|')[0]:
                        out_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 16))
                        out_label_font = out_label.font()
                        out_label_font.setUnderline(True)
                        out_label.setFont(out_label_font)
                    elif label == task.split('|')[1]:
                        out_label.setText(f"  {label}         ")
                        out_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 16))
                    elif label == task.split('|')[2]:
                        out_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 16))
                        out_label_font = out_label.font()
                        out_label_font.setItalic(True)
                        out_label.setFont(out_label_font)
                    elif label == task.split('|')[3]:
                        if '○' in label:
                            out_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 30))
                            shadow = QGraphicsDropShadowEffect(self, blurRadius=5.0,
                                                               color=QtGui.QColor("#000000"),
                                                               offset=QtCore.QPointF(0.0, 0.0))
                            out_label.setGraphicsEffect(shadow)
                        else:
                            out_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 15))
                            shadow = QGraphicsDropShadowEffect(self, blurRadius=5.0,
                                                               color=QtGui.QColor("#000000"),
                                                               offset=QtCore.QPointF(0.0, 0.0))
                            out_label.setGraphicsEffect(shadow)
                    elif label == task.split('|')[4]:
                        out_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 16))
                    labels.append(out_label)
                self.history_list.append(labels)
            self.scroll_area = QScrollArea(self)
            self.scroll_area.resize(1005, 471)
            self.scroll_area.move(26, 180)
            self.scrollAreaWidgetContents = QWidget()
            self.scrollAreaWidgetContents.setMinimumSize(900, 400)
            self.grid = QGridLayout(self.scrollAreaWidgetContents)
            self.reversed_list = self.history_list[::-1]
            for line in self.reversed_list:
                for label in line:
                    self.grid.addWidget(label, self.reversed_list.index(line), line.index(label))
            self.scroll_area.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.scroll_area.setWidget(self.scrollAreaWidgetContents)
            self.scroll_area.show()

    def view_insights(self):
        self.insights_window = InsightsWindow()
        self.insights_window.setWindowTitle('Статистика')
        self.insights_window.setFixedSize(570, 385)
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
                self.shadow = QGraphicsDropShadowEffect(self, blurRadius=5.0,
                                                        color=QtGui.QColor("#000000"), offset=QtCore.QPointF(0.0, 0.0))
                self.color_label.setGraphicsEffect(self.shadow)
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
            self.data = f"{self.start_time}| {self.task_label.text().strip()}| {self.tag_label.text()}|" \
                        f" {self.color_label.text()}| {self.time_label.text()}\n"
            cursor.execute(f"SELECT data FROM users WHERE login = '{current_login}'")
            data = cursor.fetchone()[0] + self.data
            cursor.execute(f"UPDATE users SET data = '{data}' WHERE login = '{current_login}'")
            data_base.commit()

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
        data TEXT
    )""")
    data_base.commit()
    for user in cursor.execute("SELECT * FROM users"):
        print(user)

    current_login = ''
    app = QApplication([])
    authorization = Authorization()
    authorization.show()
    toggl = MyWidget()
    sys.exit(app.exec_())
