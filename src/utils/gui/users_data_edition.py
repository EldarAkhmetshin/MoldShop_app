#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import os
from idlelib.tooltip import Hovertip
from json import loads
from os import environ

import PIL
from PIL import Image, ImageTk
from dotenv import load_dotenv, find_dotenv
import tkinter
from os.path import abspath
from tkinter import *
from tkinter import messagebox, ttk

from src.config_data.config import users
from src.data import user_rights
from src.global_values import user_data
from src.utils.logger.logs import get_info_log


def get_users_data():
    """
    Функция получения информации о пользователях из env файла
    :return: Словарь с информацией о пользователях
    """
    if not find_dotenv():
        exit('Environment variables not loaded because file .env is missing')
    else:
        load_dotenv()
        loads(environ.get('USERS'))


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
        self.scroll_y = None
        self.frame_body = None
        self.canvas = None
        self.frame_header = None
        self.password_entry_field = None
        self.login_entry_field = None

        self.delete_icon = PIL.Image.open(os.path.abspath(os.path.join('pics', 'delete.png'))) \
            .resize((20, 20))
        self.delete_icon_pil = ImageTk.PhotoImage(self.delete_icon)
        self.user_rights_icon = PIL.Image.open(os.path.abspath(os.path.join('pics', 'user_rights.png'))) \
            .resize((20, 20))
        self.user_rights_icon_pil = ImageTk.PhotoImage(self.user_rights_icon)
        self.password_icon = PIL.Image.open(os.path.abspath(os.path.join('pics', 'password.png'))) \
            .resize((20, 20))
        self.password_icon_pil = ImageTk.PhotoImage(self.password_icon)

        self.init_gui()

    def init_gui(self):
        """
        Инициация окна приложения и контейнера для размещения виджетов
        """
        self.focus_set()
        self.title('Users Data Edition')
        self.geometry('430x330')
        self.resizable(False, False)
        self.frame_header = Frame(self)
        self.frame_header.pack(fill=BOTH, expand=True)
        # Создание канвас для прикрепления к нему прокрутки / скроллинга
        self.canvas = Canvas(self)
        self.frame_body = Frame(self.canvas)
        self.frame_body.pack(fill=BOTH, expand=True)
        self.scroll_y = tkinter.Scrollbar(self, orient=tkinter.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.scroll_y.pack(side=RIGHT, fill='y')
        self.canvas.pack(fill=BOTH, expand=True)
        self.canvas.create_window((4, 4), window=self.frame_body, anchor="nw")

    def get_widgets_in_row(self, row: int, user_name: str, data: dict):
        """
        Рендер виджетов окна расположенных в одной строке
        :param data: Словарь с информацией о пользователе (пароль и права доступа)
        :param user_name: Имя пользователя
        :param row: Номер строки в окне
        """
        ttk.Label(self.frame_body, text=user_name).grid(padx=10, pady=10, column=0, row=row)
        ttk.Label(self.frame_body, text=data.get('password')).grid(padx=10, pady=10, column=1, row=row)

        password_changing_button = ttk.Button(
            self.frame_body, image=self.password_icon_pil, width=20,
            command=lambda: self.render_window_for_changing_password(user_name=user_name),
        )
        password_changing_button.grid(padx=10, pady=10, column=2, row=row)
        Hovertip(anchor_widget=password_changing_button, text='Сменить пароль', hover_delay=400)
        rights_changing_button = ttk.Button(
            self.frame_body, image=self.user_rights_icon_pil, width=20,
            command=lambda: self.render_window_for_changing_user_rights(user_name=user_name),
        )
        rights_changing_button.grid(padx=10, pady=10, column=3, row=row)
        Hovertip(anchor_widget=rights_changing_button, text='Редактировать права пользователя', hover_delay=400)
        if user_name.lower() != 'admin':
            delete_user_button = ttk.Button(
                self.frame_body, image=self.delete_icon_pil, width=20,
                command=lambda: self.delete_user(user_name=user_name),
            )
            delete_user_button.grid(padx=10, pady=10, column=4, row=row)
            Hovertip(anchor_widget=delete_user_button, text='Удалить пользователя', hover_delay=400)

    def update_window(self):
        """
        Обновление всех фреймов окна
        """
        self.destroy()
        UsersData().render_widgets()

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна авторизации пользователя
        """
        (ttk.Label(self.frame_header, text='Информация о пользователях',
                   style='Title.TLabel').pack(side=TOP, pady=7))
        # Рендер подзаголовков
        ttk.Label(self.frame_body, text='Логин', style='SubTitle.TLabel').grid(padx=10, pady=10, column=0, row=0)
        ttk.Label(self.frame_body, text='Пароль', style='SubTitle.TLabel').grid(padx=10, pady=10, column=1, row=0)

        row_num = 1
        for name, data in users.items():
            self.get_widgets_in_row(row=row_num, user_name=name, data=data)
            row_num += 1

        ttk.Button(
            self.frame_header, text='Добавить нового пользователя', style='Regular.TButton',
            width=30,
            command=self.render_window_for_new_user
        ).pack(side=TOP, padx=5, pady=8)
        # Обновление размеров канвас после добавления всех виджетов в него
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        get_info_log(user='-', message='Widgets were rendered', func_name=self.render_widgets.__name__,
                     func_path=abspath(__file__))
        # Запуск работы окна приложения
        self.mainloop()

    def delete_user(self, user_name: str):
        """
        Функция для удаления пользователя
        :param user_name: Имя пользователя
        """
        if messagebox.askyesno(title='Подтверждение',
                               message=f'Вы уверены, что хотите удалить пользователя {user_name}?',
                               parent=self):
            users.pop(user_name)
            messagebox.showinfo(title='Уведомление',
                                message='Пользователь успешно удалён',
                                parent=self)
            self.update_window()

    def render_window_for_changing_password(self, user_name: str):
        """
        Рендер окна для смены пароля
        :param user_name: Имя пользователя
        """
        window = tkinter.Toplevel()
        window.title('Password Changing')
        window.geometry('300x150')
        window.focus_set()
        window.grab_set()
        (ttk.Label(window, text=f'Введите новый пароль для пользователя: {user_name}', font=('Times', '11', 'normal'))
         .pack(side=TOP, pady=8))
        new_password = ttk.Entry(window, font=('Times', '11', 'normal'))
        new_password.pack(side=TOP, pady=8)
        ttk.Button(
            window, text='Применить', style='Regular.TButton',
            width=20,
            command=lambda: self.change_password(window=window, user_name=user_name, new_password=new_password.get())
        ).pack(side=TOP, padx=5, pady=8)
        window.mainloop()

    def render_row_widgets_for_right_changing(self, window: tkinter.Toplevel, user_name: str, right_eng: str,
                                              right_rus: str, row_num: int):
        (ttk.Label(window, text=right_rus, style='Regular.TLabel')
         .grid(padx=5, pady=4, column=0, row=row_num))
        (ttk.Label(window,
                   text='V' if users.get(user_name).get(right_eng) == 'True' else '-',
                   style='Regular.TLabel').grid(padx=5, pady=4, column=1, row=row_num))
        (ttk.Button(
            window, text='Изменить', style='Regular.TButton',
            width=20,
            command=lambda: self.change_user_right(window=window, user_name=user_name,
                                                   new_status='False'
                                                   if users.get(user_name).get(right_eng) == 'True' else 'True',
                                                   user_right=right_eng)
        ).grid(padx=5, pady=4, column=2, row=row_num))

    def render_window_for_changing_user_rights(self, user_name: str):
        """
        Рендер окна для смены и просмотра прав пользователя
        :param user_name: Имя пользователя
        """
        window = tkinter.Toplevel()
        window.title('User Rights Changing')
        window.focus_set()
        window.grab_set()

        ttk.Label(window, text=f'Право пользователя: {user_name}', style='SubTitle.TLabel').grid(padx=5, pady=4,
                                                                                                 column=0, row=0)
        ttk.Label(window, text='Статус', style='SubTitle.TLabel').grid(padx=5, pady=4, column=1, row=0)
        cnt = 1
        for right_eng, right_rus in user_rights.items():
            self.render_row_widgets_for_right_changing(window=window, user_name=user_name, right_eng=right_eng,
                                                       right_rus=right_rus, row_num=cnt)
            cnt += 1
        window.mainloop()

    def render_window_for_new_user(self):
        """
        Рендер окна для создания нового пользователя
        """
        window = tkinter.Toplevel()
        window.title('New User')
        window.focus_set()
        window.grab_set()

        ttk.Label(window, text='Новый логин пользователя:', style='Regular.TLabel').grid(padx=5, pady=4,
                                                                                         column=0, row=0)
        new_login = ttk.Entry(window, font=('Times', '11', 'normal'))
        new_login.grid(padx=5, pady=4, column=1, row=0)
        ttk.Label(window, text='Новый пароль:', style='Regular.TLabel').grid(padx=5, pady=4,
                                                                             column=0, row=1)
        new_password = ttk.Entry(window, font=('Times', '11', 'normal'))
        new_password.grid(padx=5, pady=4, column=1, row=1)

        ttk.Button(
            window, text='Применить', style='Regular.TButton', width=20,
            command=lambda: self.add_new_user(window=window, user_name=new_login.get(), password=new_password.get())
        ).grid(padx=5, pady=4, column=1, row=2)

        window.mainloop()

    def update_env_file(self):
        """
        Функция перезаписи env файла
        """
        with open(os.path.join('.env'), 'w+') as env_file:
            users_str = str(users).replace("'", '"')
            env_file.write(f"USERS='{users_str}'")
        find_dotenv()
        load_dotenv()
        messagebox.showinfo(title='Уведомление',
                            message='Изменения успешно внесены',
                            parent=self)

    def change_password(self, window: tkinter.Toplevel, user_name: str, new_password: str):
        """
        Функция изменения пароля на введённый ранее пользователем
        :param window: Окно ввода пароля
        :param user_name: Имя пользователя
        :param new_password: Новый пароль
        """

        if new_password == '' or ' ' in new_password:
            messagebox.showwarning(title='Уведомление',
                                   message='Некорректный ввод пароля (пробелов быть не должно)',
                                   parent=self)
            get_info_log(user=user_name, message='Wrong new password', func_name=self.change_password.__name__,
                         func_path=abspath(__file__))
        else:
            users[user_name]['password'] = new_password
            self.update_env_file()
            window.destroy()
            self.update_window()
            get_info_log(user=user_name, message='Password was changed', func_name=self.change_password.__name__,
                         func_path=abspath(__file__))

    def change_user_right(self, window: tkinter.Toplevel, user_name: str, user_right: str, new_status: str):
        """
        Функция изменения одного из прав пользователя
        :param window: Окно ввода пароля
        :param user_name: Имя пользователя
        :param user_right: Право пользователя
        :param new_status: Строковое значение ("True" или "False")
        характеризующее наличие доступа к определённым функциям ("user_right")
        """
        users.get(user_name)[user_right] = new_status
        self.update_env_file()
        window.destroy()
        self.render_window_for_changing_user_rights(user_name)
        get_info_log(user=user_name, message='User right was changed', func_name=self.change_user_right.__name__,
                     func_path=abspath(__file__))

    def add_new_user(self, window: tkinter.Toplevel, user_name: str, password: str):
        """
        Функция валидации и создания нового пользователя
        :param window: Окно ввода данных
        :param user_name: Новое имя пользователя
        :param password: Новый пароль
        """
        if user_name == '' or ' ' in user_name:
            messagebox.showwarning(title='Уведомление',
                                   message='Некорректный ввод имени пользователя (пробелов быть не должно)',
                                   parent=self)
            get_info_log(user=user_name, message='Wrong new user_name', func_name=self.add_new_user.__name__,
                         func_path=abspath(__file__))
            return

        if users.get(user_name):
            messagebox.showwarning(title='Уведомление',
                                   message='Логин с таким именем уже существует',
                                   parent=self)
            get_info_log(user=user_name, message='Wrong new user_name', func_name=self.add_new_user.__name__,
                         func_path=abspath(__file__))
            return

        if password == '' or ' ' in password:
            messagebox.showwarning(title='Уведомление',
                                   message='Некорректный ввод пароля (пробелов быть не должно)',
                                   parent=self)
            get_info_log(user=user_name, message='Wrong new password', func_name=self.add_new_user.__name__,
                         func_path=abspath(__file__))
            return

        users[user_name] = {'password': password}
        for right in user_rights.keys():
            users.get(user_name)[right] = 'False'

        self.update_env_file()
        window.destroy()

        get_info_log(user=user_name, message='New user was added', func_name=self.add_new_user.__name__,
                     func_path=abspath(__file__))

        self.update_window()

