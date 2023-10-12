#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import os
import sqlite3
import tkinter
from tkinter import *
from tkinter import messagebox, ttk
from tkinter.ttk import Frame
from typing import Callable
from PIL import ImageTk
from pdf2image import convert_from_path

from src.config_data.config import passwords
from src.global_values import user_data
from src.utils.sql_database import table_funcs


class Attachment(tkinter.Toplevel):
    """
    Класс представляет набор функций для создания графического интерфейса дополнительного окна просмотра вложенных файлов, 
    редактирования, их предпросмотра и скачивания в указанную директорию пользователем
    """

    def __init__(self, mold_number: str, part_number: str = None, hot_runner: bool = None):
        """
        Создание переменных
        """
        self.mold_number = mold_number
        self. part_number = part_number
        self.hot_runner = hot_runner
        self.input_error_label = None
        self.image = None
        self.image_pil = None
        self.frame = None
        super().__init__()
        self.init_gui()

    def init_gui(self):
        """
        Инициация окна приложения и контейнера для размещения виджетов
        """
        self.focus_set()
        self.grab_set()
        self.frame_header = Frame(self)
        self.frame_body = Frame(self)
        self.frame.pack()

    def get_label_and_entry_widgets_in_row(self, text: str, row: int):
        """
        Рендер виджетов окна расположенных в одной строке
        :param text: Текст надписи
        :param row: Номер строки в окне
        """
        ttk.Label(self.frame_body, text=text, style='Regular.TLabel').grid(column=1, row=row, padx=5, pady=5)
        ttk.Button(
            self.frame_body, text='Загрузить', style='Regular.TButton',
            command=lambda: self.download_file(filename=text)
        ).grid(padx=10, pady=10, column=2, row=row)
        ttk.Button(
            self.frame_body, text='Предпросмотр', style='Regular.TButton',
            command=lambda: self.preview_file(filename=text)
        ).grid(padx=10, pady=10, column=3, row=row)
        ttk.Button(
            self.frame_body, text='Удалить вложение', style='Regular.TButton',
            width=20, command=lambda: self.delete_file(filename=text)
        ).grid(padx=10, pady=10, column=3, row=row)

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна ввода информации
        """
        ttk.Label(self.frame_header, text='Просмотр вложенных файлов', style='Title.TLabel').pack(side=TOP, pady=15)

        # Запуск работы окна приложения
        self.mainloop()

    def download_file(self, filename: str):
        pass

    def open_additional_preview_window(self, filename: str):
        self.image = Image.open(os.path.abspath(os.path.join('..', 'pics', filename))) \
            .resize((1024, 768))
        self.image_pil = ImageTk.PhotoImage(self.image)
        window = tkinter.Toplevel()
        window.title('Preview')
        window.geometry('1024x768')
        window.resizable(False, False)
        (Label(window, image=self.image_pil)
         .pack(side=TOP, pady=5))

    def preview_file(self, filename):
        if '.pdf' in filename:
            pages = convert_from_path(os.path.abspath(os.path.join('..', 'pics', filename)))
            for i in range(len(pages)):
                page_name = f'page{i}.jpg'
                pages[i].save(page_name, 'JPEG')
                self.open_additional_preview_window(page_name)
                os.remove(os.path.abspath(os.path.join('..', 'pics', page_name)))
        elif ('.jpg' or '.jpeg' or '.png') in filename:
            self.open_additional_preview_window(filename)

    def delete_file(self, filename: str):
        pass
