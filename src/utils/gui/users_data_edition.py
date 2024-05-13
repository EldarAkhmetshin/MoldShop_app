#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import os
from json import loads
from os import environ
from dotenv import load_dotenv, find_dotenv
import time
import tkinter
from os.path import abspath
from tkinter import *
from tkinter import messagebox, ttk

from src.config_data.config import users
from src.data import user_rights
from src.global_values import user_data
from src.utils.logger.logs import get_info_log


def get_users_data() -> dict:
    """
    Функция получения информации о пользователях из env файла
    :return: Словарь с информацией о пользователях
    """
    if not find_dotenv():
        exit('Environment variables not loaded because file .env is missing')
    else:
        load_dotenv()
        # with open(os.path.join('.env'), 'w+') as env_file:
        #     users_str = str(users).replace("'", '"')
        #     env_file.write(f"USERS='{users_str}'")
        return loads(environ.get('USERS'))

class UsersData(tkinter.Toplevel):
    """
    Класс представляет набор функций для создания графического интерфейса окна авторизации пользователя с помощью
    библиотеки Tkinter. Также осуществляется проверка введённых данных пользователем.
    """

    def __init__(self):
        """
        Создание переменных
        """
        super().__init__()
        self.users = get_users_data()
        self.scroll_y = None
        self.frame_body = None
        self.canvas = None
        self.frame_header = None
        self.password_entry_field = None
        self.login_entry_field = None
        self.init_gui()

    def init_gui(self):
        """
        Инициация окна приложения и контейнера для размещения виджетов
        """
        self.focus_set()
        self.title('Users Data Edition')
        self.geometry('1200x500')
        self.frame_header = Frame(self)
        self.frame_header.pack(fill=BOTH, expand=True)
        # создание канвас для прикрпеления к нему прокрутки / скроллинга
        self.canvas = Canvas(self)
        self.frame_body = Frame(self.canvas)
        self.frame_body.pack(fill=BOTH, expand=True)
        self.scroll_y = tkinter.Scrollbar(self, orient=tkinter.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.scroll_y.pack(side=RIGHT, fill='y')
        self.canvas.pack(fill=BOTH, expand=True)
        self.canvas.create_window((4, 4), window=self.frame_body, anchor="nw")

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
                self.destroy()
                get_info_log(user=user_name, message='Successful login', func_name=self.check_entry_user_data.__name__,
                             func_path=abspath(__file__))
                time.sleep(0.3)
            # Если данные введены некорректно пользователь получит уведомление об ошибке
            else:
                messagebox.showerror('Ошибка', 'Не верный пароль!')
                self.login_entry_field.delete(0, END)
                self.password_entry_field.delete(0, END)

    def get_widgets_in_row(self, row: int, user_name: str, user_data: dict):
        """
        Рендер виджетов окна расположенных в одной строке
        :param user_data: Словарь с информацией о пользователе (пароль и права доступа)
        :param user_name: Имя пользователя
        :param row: Номер строки в окне
        """
        cnt = 0
        ttk.Label(self.frame_body, text=user_name).grid(padx=10, pady=10, column=cnt, row=row)
        for cnt, info in enumerate(user_data.values()):
            ttk.Label(self.frame_body, text=info).grid(padx=10, pady=10, column=cnt + 1, row=row)

        (ttk.Button(
            self.frame_body, text='Редактировать пользователя', style='Regular.TButton', width=10)
         .grid(padx=10, pady=10, column=cnt + 2, row=row))
        (ttk.Button(
            self.frame_body, text='Удалить пользователя', style='Regular.TButton',
            width=20)
         .grid(padx=10, pady=10, column=cnt + 3, row=row))

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна авторизации пользователя
        """
        (ttk.Label(self.frame_header, text='Информация о пользователях',
                   style='Title.TLabel').pack(side=TOP, pady=7))
        # Рендер подзаголовков
        ttk.Label(self.frame_body, text='Логин', style='SubTitle.TLabel').grid(padx=10, pady=10, column=0, row=0)
        ttk.Label(self.frame_body, text='Пароль', style='SubTitle.TLabel').grid(padx=10, pady=10, column=1, row=0)
        for num, right in enumerate(user_rights.values()):
            (ttk.Label(self.frame_body, text=right, style='SubTitle.TLabel')
             .grid(padx=10, pady=10, column=num + 2, row=0))
        row_num = 1
        for name, data in users.items():
            print(name, data)
            self.get_widgets_in_row(row=row_num, user_name=name, user_data=data)
            row_num += 1
        # Обновление размеров канваса после добавления всех виджетов в него
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        get_info_log(user='-', message='Widgets were rendered', func_name=self.render_widgets.__name__,
                     func_path=abspath(__file__))
        # Запуск работы окна приложения
        self.mainloop()

