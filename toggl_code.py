from functools import partial

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QApplication, QScrollArea, \
    QColorDialog, QErrorMessage, QGridLayout, QLineEdit, QCheckBox, QTableWidgetItem, \
    QHeaderView
from PyQt5.QtCore import QTimer
import time
import datetime
from pyqtgraph.Qt import QtCore, QtGui
import sqlite3
import sys


class Authorization(QWidget):
    """"Класс для входа в аккаунт или регистрации в приложении"""

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
        """Функция, которая показывает или скрывает пароль"""
        if self.eye_button.isChecked():
            self.eye_button.setStyleSheet("background-color: rgb(195, 195, 195)")
            self.password.setEchoMode(QLineEdit.Normal)
        else:
            self.eye_button.setStyleSheet("background-color: rgb(127, 127, 127)")
            self.password.setEchoMode(QLineEdit.Password)

    def next_window(self):
        """Функция, которая открывает окно приложения, если выполнен вход"""
        if self.logged_in:
            self.error_message_label.setStyleSheet("color: rgb(127, 127, 127)")
            self.close()
            toggl.show()
            toggl.start_func()
        else:
            self.error_message_label.setText('Сначала войдите в аккаунт.')
            self.error_message_label.setStyleSheet("color: rgb(255, 0, 0)")

    def log_in(self):
        """Функция, которая производит вход пользователя в систему"""
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
                    cursor.execute(f"SELECT id from users where login = '{user_login}'")
                    u_id = cursor.fetchone()[0]
                    self.error_message_label.setStyleSheet("color: rgb(0, 255, 0)")
                    password_flag = 0
                    self.logged_in = True
                    global user_id
                    user_id = u_id
                    break
            if password_flag == 1:
                return

    def sign_up(self):
        """Функция, которая регистрирует нового пользователя"""
        user_login = self.login.text()
        user_password = self.password.text()

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
            cursor.execute("INSERT INTO users VALUES (NULL, ?, ?)", (user_login, user_password))
            cursor.execute(f"SELECT id FROM users WHERE login = '{user_login}'")
            global user_id
            user_id = cursor.fetchone()[0]
            data_base.commit()
            self.error_message_label.setText('Вы успешно зарегистрированы.')
            self.error_message_label.setStyleSheet("color: rgb(0, 255, 0)")
        else:
            self.error_message_label.setText('Такой логин уже существует. Попробуйте снова.')
            self.error_message_label.setStyleSheet("color: rgb(255, 0, 0)")
            return


class InsightsWindow(QWidget):
    """Класс, который показывает статистику пользователя"""

    def __init__(self):
        super().__init__()
        uic.loadUi('toggl_insights.ui', self)
        cursor.execute(f"SELECT start_time, time FROM data WHERE user_id = '{user_id}'")
        self.data = cursor.fetchall()
        if not self.data:
            self.insights_label.setText('Нет данных для составления вашей статистики.')
            self.insights_label.move(10, 150)
            self.insights_label_2.setStyleSheet("color: rgb(190, 190, 190)")
            self.insights_label_3.setStyleSheet("color: rgb(190, 190, 190)")
        else:
            self.date_list = {}
            self.list_of_values = []
            self.count_statistics()
            self.insights_label.setText('Ваша статистика:')
            self.insights_label.move(10, 10)
            self.insights_label_2.setStyleSheet("color: rgb(0, 0, 0)")
            self.insights_label_3.setStyleSheet("color: rgb(0, 0, 0)")
            self.insights_scroll_area = QScrollArea(self)
            self.insights_scroll_area.resize(530, 310)
            self.insights_scroll_area.move(20, 75)
            self.insights_scroll_area.setStyleSheet("background-color: rgb(255, 255, 255)")
            self.scrollAreaWidgetContents1 = QWidget()
            self.scrollAreaWidgetContents1.setMinimumSize(510, 280)
            self.insights_grid = QGridLayout(self.scrollAreaWidgetContents1)
            n = 0
            items = list(self.date_list.items())
            reversed_dict = {k: v for k, v in reversed(items)}
            for dates, times in reversed_dict.items():
                date_label = QLabel(dates)
                date_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 15))
                time_label = QLabel(f"\t\t{times}")
                time_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 15))
                self.insights_grid.addWidget(date_label, n, 0)
                self.insights_grid.addWidget(time_label, n, 1)
                n += 1
            self.insights_scroll_area.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.insights_scroll_area.setWidget(self.scrollAreaWidgetContents1)
            self.insights_scroll_area.show()

    def count_statistics(self):
        """Функция, которая подсчитывает статитстику"""
        for line in self.data:
            value = line[0][:10]
            time_value = line[1]
            if value not in self.date_list.keys():
                self.date_list[value] = time_value
            else:
                previous_time_value = self.date_list[value]
                previous_hours_value = int(previous_time_value[:2])
                hours_value = int(time_value[:2])
                previous_minutes_value = int(previous_time_value[3:5])
                minutes_value = int(time_value[3:5])
                previous_seconds_value = int(previous_time_value[6:])
                seconds_value = int(time_value[6:])
                hours_value = hours_value + previous_hours_value
                minutes_value = minutes_value + previous_minutes_value
                seconds_value = seconds_value + previous_seconds_value
                while minutes_value > 59 or seconds_value > 59:
                    if seconds_value > 59:
                        minutes_value = minutes_value + 1
                        seconds_value = abs(60 - seconds_value)
                    if minutes_value > 59:
                        hours_value = hours_value + 1
                        minutes_value = abs(60 - minutes_value)
                time_value = QtCore.QTime(hours_value, minutes_value, seconds_value).toString("hh:mm:ss")
                self.date_list[value] = f'{time_value}'


class PlansWindow(QWidget):
    """Класс, который показывает планы пользоваетеля"""

    def __init__(self):
        super().__init__()
        uic.loadUi('toggl_plans.ui', self)
        cursor.execute(f"SELECT plan FROM plans WHERE user_id = '{user_id}'")
        plans0 = cursor.fetchall()
        plans = []
        for plan in plans0:
            plans.append(plan[0])
        self.plans_scroll_area = QScrollArea(self)
        self.plans_scroll_area.resize(461, 351)
        self.plans_scroll_area.move(10, 120)
        self.scrollAreaWidgetContents2 = QWidget()
        self.scrollAreaWidgetContents2.setMinimumSize(455, 345)
        self.plans_grid = QGridLayout(self.scrollAreaWidgetContents2)
        self.plans_dict = {}
        self.add_button.clicked.connect(self.add_plan)
        self.list_of_plans = plans
        self.display_plans()

    def display_plans(self):
        """Функция, которая выводит список планов в ScrollArea"""
        self.plans_scroll_area = QScrollArea(self)
        self.plans_scroll_area.resize(461, 351)
        self.plans_scroll_area.move(10, 120)
        self.plans_scroll_area.setStyleSheet("background-color: white")
        self.scrollAreaWidgetContents2 = QWidget()
        self.scrollAreaWidgetContents2.setMinimumSize(455, 345)
        self.plans_grid = QGridLayout(self.scrollAreaWidgetContents2)
        self.reserved_plans = self.list_of_plans[::-1]
        n = 0
        for plan in self.reserved_plans:
            if plan == '':
                continue
            else:
                plan_label = QLabel(plan)
                plan_label.setFont(QtGui.QFont('Bahnschrift Light SemiCondensed', 15))
                check_box = QCheckBox()
                check_box.resize(20, 20)
                self.plans_grid.addWidget(check_box, n, 0)
                self.plans_grid.addWidget(plan_label, n, 1)
                n += 1
                self.plans_dict[check_box] = plan_label
                check_box.stateChanged.connect(self.delete_plan)
        self.plans_scroll_area.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        self.plans_scroll_area.setWidget(self.scrollAreaWidgetContents2)
        self.plans_scroll_area.show()

    def add_plan(self):
        """Функция, которая добавляет новые планы"""
        if self.current_plan.text() == '':
            self.error_dialog = QErrorMessage()
            self.error_dialog.showMessage('Вам нужно обязательно ввести что-нибудь в поле.')
            self.error_dialog.show()
            return
        else:
            plan_text = self.current_plan.text()
            cursor.execute(f"INSERT INTO plans VALUES (?, ?)", (user_id, plan_text))
            data_base.commit()
            self.list_of_plans.append(self.current_plan.text())
            self.display_plans()
            self.current_plan.setText('')

    def delete_plan(self):
        """Функция, которая удаляет планы из списка"""
        sender = self.sender()
        plan_to_delete = self.plans_dict[sender]
        self.list_of_plans.remove(plan_to_delete.text())
        cursor.execute(f"DELETE FROM plans WHERE plan = '{plan_to_delete.text()}'")
        data_base.commit()
        self.display_plans()


class Timers:
    """Класс, который создаёт новые таймеры"""

    def __init__(self, sender, row, col, data_table):
        self.data_table = data_table
        self.sender = sender
        self.row = row
        self.col = col
        cursor.execute(f'SELECT time from data WHERE checkbox = "{self.sender}"')
        line = cursor.fetchone()[0]
        h, m, s = int(line[:2]), int(line[3:5]), int(line[6:])
        self.timer_ = QtCore.QTimer()
        self.curr_time = QtCore.QTime(h, m, s)
        self.timer_.setInterval(1000)
        self.timer_.timeout.connect(self.time_add)

    def start_timer(self):
        """Функция, котороя запускает таймеры"""
        self.timer_.start()

    def stop_timer(self):
        """Функция, которая останавливает таймеры"""
        self.timer_.stop()

    def time_add(self):
        """Функция, которая добавляет секунлы"""
        global flag
        flag = True
        self.curr_time = self.curr_time.addSecs(1)
        self.data_table.setItem(self.row, self.col, QTableWidgetItem(self.curr_time.toString("hh:mm:ss")))
        cursor.execute(
            f"UPDATE data SET time = '{self.data_table.item(self.row, self.col).text()}' WHERE checkbox = '{self.sender}'")
        data_base.commit()


class MyWidget(QMainWindow):
    """Класс основного окна программы"""

    def __init__(self):
        super().__init__()
        uic.loadUi('toggl_app.ui', self)
        self.setWindowTitle("Toggl")
        self.setFixedSize(1062, 676)
        self.history_list = []

        self.color = ''

        self.select_color.move(640, 60)

        self.insights_button.clicked.connect(self.view_insights)
        self.plans_button.clicked.connect(self.view_plans)

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
        self.stop.clicked.connect(self.check_timers)

        self.data_table.setColumnCount(6)
        self.data_table.setHorizontalHeaderLabels(["Начало", "Задача", "Тэг", "Цвет", "Длительность", "Продолжить"])

    def continue_task(self, timer):
        """Функция, которая создаёт таймеры"""
        sender = self.sender()
        timer0 = timer
        global flag
        if sender.isChecked():
            flag = True
            timer0.start_timer()
        else:
            flag = False
            timer0.stop_timer()

    def add_content(self, data):
        """Функция, которая добавляет данные в таблицу"""
        self.data_table.setVisible(True)
        self.data_table.setRowCount(len(data))
        row_id = 0
        for row in data:
            for i in range(6):
                if i == 3:
                    color = row[4]
                    if color == '#ffffff':
                        color_label = QLabel('○')
                    else:
                        color_label = QLabel(f'<h1 style="color: {color};">●')
                    self.data_table.setCellWidget(row_id, 3, color_label)
                elif i == 5:
                    btn = QCheckBox()
                    cursor.execute(f"UPDATE data SET checkbox = '{btn}' WHERE start_time = '{row[1]}'")
                    data_base.commit()
                    cb_timer = Timers(btn, row_id, i - 1, self.data_table)
                    btn.stateChanged.connect(partial(self.continue_task, timer=cb_timer))
                    self.data_table.setCellWidget(row_id, 5, btn)
                else:
                    self.data_table.setItem(row_id, i, QTableWidgetItem(str(row[i + 1])))
            row_id += 1
        self.data_table.resizeColumnsToContents()
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.data_table.update()

    def start_func(self):
        """Функция, которая выводит данные пользователя, если они уже есть"""
        cursor.execute(f"SELECT * FROM data WHERE user_id = '{user_id}'")
        data = cursor.fetchall()
        if len(data) == 0:
            self.data_table.setVisible(False)
            self.start_text.setStyleSheet("color: rgb(0, 0, 0)")
        else:
            self.add_content(data[::-1])

    def view_insights(self):
        """Функция, которая запускает окно со статистикой"""
        self.insights_window = InsightsWindow()
        self.insights_window.setWindowTitle('Статистика')
        self.insights_window.setFixedSize(570, 385)
        self.insights_window.show()

    def view_plans(self):
        """Функия, которая запускает окно с планами"""
        self.plans_window = PlansWindow()
        self.plans_window.setWindowTitle('Ваши планы')
        self.plans_window.setFixedSize(480, 490)
        self.plans_window.show()

    def current_time(self):
        """Функция, которая регистрирует время начала выполнения задачи"""
        if '' == self.task.text():
            self.error_dialog = QErrorMessage()
            self.error_dialog.showMessage('Вам нужно обязательно ввести название задачи.')
            self.error_dialog.show()
            self.timerUp.stop()
            self.reset()
            return
        else:
            self.start_time = datetime.datetime.now()
            self.start_time = self.start_time.strftime("%d-%m-%Y %H:%M:%S")

    def check_timers(self):
        if flag == True:
            self.error_dialog = QErrorMessage()
            self.error_dialog.showMessage('Сначала остановите другие таймеры.')
            self.error_dialog.show()
            return
        else:
            self.timerUp.stop()
            self.newtask()
            self.reset()


    def updateUptime(self):
        """Функция, которая обновляет таймер"""
        self.time += 1
        self.settimer(self.time)

    def settimer(self, int):
        """Функция, которая передаёт значения таймера в Label"""
        self.time = int
        self.timelabel.setText(time.strftime('%H:%M:%S', time.gmtime(self.time)))

    def reset(self):
        """Функция, которая сбивает таймер"""
        self.time = 0
        self.settimer(self.time)

    def newtask(self):
        """Функция, которая добавляет новую задачу"""
        if '00:00:00' == self.timelabel.text() or '' == self.task.text():
            return
        else:
            if self.no_color.isChecked():
                self.color = '#ffffff'
            data_list = [user_id, self.start_time, self.task.text(), '#' + self.tag.text(),
                 self.color, time.strftime("%H:%M:%S", time.gmtime(self.time)), '']
            self.selected_color.setStyleSheet("color: rgb(127, 127, 127)")
            cursor.execute("INSERT INTO data VALUES (?, ?, ?, ?, ?, ?, ?)", (data_list))
            data_base.commit()
            cursor.execute(f"SELECT * FROM data WHERE user_id = '{user_id}'")
            data = cursor.fetchall()
            self.add_content(data[::-1])
            self.history_list.append(data_list[1:-1])
            self.task.setText('')
            self.tag.setText('')
            if not self.no_color.isChecked():
                self.no_color.toggle()

    def no_color_clicked(self):
        """Функция, которая прячет Label с выбранным цветом, если выбран параметр 'без цвета'"""
        self.selected_color.setStyleSheet("color: rgb(127, 127, 127)")

    def color_selection(self):
        """Функция, которая запускает окно выбора цвета"""
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
    data_base = sqlite3.connect('toggl_db.sqlite3')
    cursor = data_base.cursor()
    user_id = 0
    flag = False
    app = QApplication([])
    authorization = Authorization()
    authorization.show()
    toggl = MyWidget()
    sys.exit(app.exec_())