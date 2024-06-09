#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import time
import tkinter
from os.path import abspath
from tkinter import *
from tkinter import messagebox, ttk

from dataclasses import dataclass

from src.config_data.config import users
from src.global_values import user_data
from src.utils.logger.logs import get_info_log, get_warning_log


def change_user(window: tkinter.Tk):
    """
    Функция смены действующего пользователя в приложении
    :param window: Окно приложения
    """
    from src.__main__ import log_in_app, render_main_window

    window.destroy()
    user_data.clear()
    log_in_app()
    if user_data.get('access'):
        render_main_window()

@dataclass
class LogInApp(Frame):
    """
    Класс представляет набор функций для создания графического интерфейса окна авторизации пользователя с помощью
    библиотеки Tkinter. Также осуществляется проверка введённых данных пользователем.
    """
    window: tkinter.Tk
    password_entry_field: tkinter.ttk.Entry = None
    login_entry_field: tkinter.ttk.Entry = None

    def __post_init__(self):
        """
        Инициация окна приложения и контейнера для размещения виджетов
        """
        super().__init__()
        self.master.title('MoldShop Management')
        self.pack(fill=BOTH, expand=True)
        self.login_frame: tkinter.Frame = Frame(self)
        self.login_frame.pack()

    def check_entry_user_data(self):
        """
        Функция проверки введённых данных пользователем
        """
        # Окно авторизации закрывается если пароль введён правильно
        user_name = self.login_entry_field.get()
        try:
            users.get(user_name).get('password')
        except AttributeError:
            messagebox.showerror('Ошибка', 'Не верный логин!')
        else:
            if users.get(user_name).get('password') == self.password_entry_field.get():
                # Сохранение информации о пользователе в глобальную переменную
                user_data['user_name'] = user_name
                user_data['access'] = True
                user_data['stock_changing_in'] = users.get(user_name).get('stock_changing_in')
                user_data['stock_changing_out'] = users.get(user_name).get('stock_changing_out')
                user_data['mold_status_changing'] = users.get(user_name).get('mold_status_changing')
                user_data['molds_and_boms_data_changing'] = users.get(user_name).get('molds_and_boms_data_changing')
                user_data['attachments_changing'] = users.get(user_name).get('attachments_changing')
                user_data['purchased_parts_uploading'] = users.get(user_name).get('purchased_parts_uploading')
                self.window.destroy()
                get_info_log(user=user_name, message='Successful login', func_name=self.check_entry_user_data.__name__,
                             func_path=abspath(__file__))
                time.sleep(0.3)
            # Если данные введены некорректно пользователь получит уведомление об ошибке
            else:
                messagebox.showerror('Ошибка', 'Не верный пароль!')
                self.login_entry_field.delete(0, END)
                self.password_entry_field.delete(0, END)
                get_warning_log(user=user_name, message='Not correct login or password',
                                func_name=self.check_entry_user_data.__name__,
                                func_path=abspath(__file__))

    def on_pressed_key(self, event):
        """
        Обработчик события нажатия клавиши Enter
        :param event: Обрабатываемое событие
        """
        self.check_entry_user_data()

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна авторизации пользователя
        """
        (ttk.Label(self.login_frame, text='Уважаемый пользователь, \nавторизуйтесь для входа в систему',
                   style='Regular.TLabel')
         .grid(column=2, row=1, pady=15))

        ttk.Label(self.login_frame, text='Логин:', style='Regular.TLabel').grid(column=1, row=2, padx=5, pady=5)
        ttk.Label(self.login_frame, text='Пароль:', style='Regular.TLabel').grid(column=1, row=3, padx=5, pady=5)

        self.login_entry_field = ttk.Entry(self.login_frame, font=('Arial', '10', 'normal'))
        self.login_entry_field.grid(padx=5, pady=5, column=2, row=2)
        self.password_entry_field = ttk.Entry(self.login_frame, show='*', font=('Arial', '10', 'normal'))
        self.password_entry_field.grid(padx=5, pady=5, column=2, row=3)

        ttk.Button(
            self.login_frame, text='Войти', style='Regular.TButton',
            command=lambda: self.check_entry_user_data()
        ).grid(padx=10, pady=10, column=2, row=4)

        # Запуск работы окна приложения
        get_info_log(user='-', message='Login widgets were rendered', func_name=self.render_widgets.__name__,
                     func_path=abspath(__file__))

        self.window.mainloop()
