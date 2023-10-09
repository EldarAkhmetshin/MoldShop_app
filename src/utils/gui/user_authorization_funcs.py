#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import time
import tkinter
from os.path import abspath
from tkinter import *
from tkinter import ttk

#from tkinter import messagebox

from tkinter import messagebox, ttk
#from tkinter.ttk import Frame

from src.config_data.config import passwords
from src.global_values import user_data
from src.utils.logger.logs import get_info_log


class LogInApp(Frame):
    """
    Класс представляет набор функций для создания графического интерфейса окна авторизации пользователя с помощью
    библиотеки Tkinter. Также осуществляется проверка введённых данных пользователем.
    """

    def __init__(self, window: tkinter.Tk):
        """
        Создание переменных
        :param window: Окно приложения
        self.password_entry_field: Поле ввода пароля
        self.login_entry_field: Поле ввода логина
        self.login_frame: Контейнер для размещения виджетов (кнопок, надписей и т.д.)
        """
        self.window = window
        self.password_entry_field = None
        self.login_entry_field = None
        self.login_frame = None
        super().__init__()
        self.init_gui()

    def init_gui(self):
        """
        Инициация окна приложения и контенера для размещения виджетов
        """
        self.master.title('MoldShop Management')
        self.pack(fill=BOTH, expand=True)
        self.login_frame = Frame(self)
        self.login_frame.pack()

    def check_entry_user_data(self):
        """
        Фнкция проверки введённых данных пользователем
        """
        # Окно авторизации закрывается если пароль введён правильно
        user_name = self.login_entry_field.get()
        if passwords.get(f'user_{user_name}_password') == self.password_entry_field.get():
            user_data['user_name'] = user_name
            user_data['access'] = True
            self.window.destroy()
            get_info_log(user=user_name, message='Successful login', func_name=self.check_entry_user_data.__name__,
                         func_path=abspath(__file__))
            time.sleep(0.3)
        # Если данные введены некорректно пользователь получит уведомление об ошибке
        else:
            messagebox.showerror('Уведомление об ошибке', 'Не верный пароль!')
            self.login_entry_field.delete(0, END)
            self.password_entry_field.delete(0, END)

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

        get_info_log(user='-', message='Login widgets were rendered', func_name=self.render_widgets.__name__,
                     func_path=abspath(__file__))
        # Запуск работы окна приложения
        self.window.mainloop()

