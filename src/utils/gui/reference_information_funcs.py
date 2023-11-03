#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import os
import tkinter
from os.path import abspath
from tkinter import *
from tkhtmlview import HTMLLabel
from tkinter import ttk
from PIL import Image, ImageTk
from typing import Callable

from src.global_values import user_data
from src.utils.logger.logs import get_info_log
from src.data import user_rights, instructions


def check_user_rigths() -> str:
    define_answer: Callable = lambda: 'Да' if user_data.get(name) == 'True' else 'Нет'
    result = ''
    for name, description in user_rights.items():
        result = f'{result}\n\t{description}: {define_answer()}'
    return result


class ReferenceInfo(tkinter.Toplevel):
    """
    Класс представляет набор функций для вывода справочной информации о приложении
    """

    def __init__(self, app_info: bool = None):
        """
        Создание переменных
        :param app_info: Булево значение, принимающее значение True, когда необходимо вывести инфо о приложении
        """
        self.frame_additional = None
        self.app_info = app_info
        self.frame_header = None
        self.frame_body = None
        self.frame_bottom = None
        self.image_logo = Image.open(os.path.abspath(os.path.join('pics', 'company_logo.png'))) \
            .resize((150, 70))
        self.image_logo_pil = ImageTk.PhotoImage(self.image_logo)
        self.back_icon = Image.open(os.path.abspath(os.path.join('pics', 'back.png'))) \
            .resize((20, 20))
        self.back_icon_pil = ImageTk.PhotoImage(self.back_icon)
        super().__init__()
        self.init_gui()

    def init_gui(self):
        """
        Инициация окна приложения и контенера для размещения виджетов
        """
        self.focus_set()
        self.frame_header = Frame(self, relief=RIDGE)
        self.frame_header.pack(side=TOP, padx=0)
        self.frame_body = Frame(self)
        self.frame_body.pack(fill=BOTH, expand=True)
        self.frame_bottom = Frame(self)
        self.frame_bottom.pack(fill=BOTH, expand=True)

    def clear_frames(self):
        for widget in self.frame_header.winfo_children():
            widget.destroy()
        for widget in self.frame_body.winfo_children():
            widget.destroy()
        for widget in self.frame_bottom.winfo_children():
            widget.destroy()
        self.frame_header.pack_forget()
        self.frame_body.pack_forget()
        self.frame_bottom.pack_forget()
        self.init_gui()

    def show_instruction(self, instruction: str):
        """
        Функция для отображения инструкции в HTML виде
        :param instruction: Инструкция для пользователя обёрнутая в HTML разметку
        """
        self.clear_frames()
        HTMLLabel(self.frame_body, html=instruction).pack(side=TOP, padx=5, pady=5)
        ttk.Button(self.frame_bottom, image=self.back_icon_pil,
                   command=self.render_widgets()).pack(side=LEFT, padx=5, pady=2)

    def back_to_main_page(self):
        """
        Функция для рендера главной странницы справки когда пользователь нажал Назад
        """
        self.clear_frames()
        self.render_widgets()

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна авторизации пользователя
        """
        if self.app_info:
            ttk.Label(self.frame_header, image=self.image_logo_pil).pack(side=TOP, padx=5, pady=5)
            ttk.Label(self.frame_body, text='\nПриложение: ArtPack MoldShop Manadgment'
                                            '\nВерсия: 1.0.0 от 08.11.23'
                                            '\nТребования: ОС Windows; 64-bit'
                                            f'\nПользователь: {user_data.get("user_name")}'
                                            f'\nПрава пользователя:'
                                            f'{check_user_rigths()}',
                      style='Regular.TLabel').pack(side=LEFT, padx=5, pady=5)
        else:
            ttk.Label(self.frame_header, text='Справочная информация', style='Title.TLabel').pack(side=TOP, padx=5,
                                                                                                  pady=5)
            ttk.Button(self.frame_body, text='Основные возможности приложения',
                       command=lambda: self.show_instruction(f'{instructions.get("app_possibilities")}'),
                       width=28, style='Regular.TButton').pack(side=TOP, padx=5, pady=5)
            ttk.Button(self.frame_body, text='Взаимодействие со складом',
                       command=lambda: self.show_instruction(f'{instructions.get("warehouse_operations")}'),
                       width=28, style='Regular.TButton').pack(side=TOP, padx=5, pady=5)
            ttk.Button(self.frame_body, text='Перемещение пресс-форм',
                       command=lambda: self.show_instruction(f'{instructions.get("molds_moving")}'),
                       width=28, style='Regular.TButton').pack(side=TOP, padx=5, pady=5)
            ttk.Button(self.frame_body, text='Работа с вложениями',
                       command=lambda: self.show_instruction(f'{instructions.get("attachments")}'),
                       width=28, style='Regular.TButton').pack(side=TOP, padx=5, pady=5)
            ttk.Button(self.frame_body, text='Загрузка нового BOM',
                       command=lambda: self.show_instruction(f'{instructions.get("new_bom_uploading")}'),
                       width=28, style='Regular.TButton').pack(side=TOP, padx=5, pady=5)

        get_info_log(user='-', message='Reference info widgets were rendered', func_name=self.render_widgets.__name__,
                     func_path=abspath(__file__))
        # Запуск работы окна приложения
        self.mainloop()
