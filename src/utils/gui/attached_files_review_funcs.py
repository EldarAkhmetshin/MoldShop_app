#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import os
import sqlite3
import tkinter
from tkinter import *
from tkinter import messagebox, ttk
from tkinter.ttk import Frame
from typing import Callable
from PIL import ImageTk, Image
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
        self.frame_body = None
        self.frame_header = None
        self.mold_number = mold_number
        self.part_number = part_number
        self.hot_runner = hot_runner
        self.input_error_label = None
        self.image = None
        self.image_pil = None
        self.frame = None
        self.root = None
        super().__init__()
        self.init_gui()

    def init_gui(self):
        """
        Инициация окна приложения и контейнера для размещения виджетов
        """
        self.focus_set()
        self.frame_header = Frame(self)
        self.frame_header.pack(fill=BOTH, expand=True)
        self.frame_body = Frame(self)
        self.frame_body.pack(fill=BOTH, expand=True)

    def get_label_and_entry_widgets_in_row(self, text: str, row: int, root: str):
        """
        Рендер виджетов окна расположенных в одной строке
        :param root:
        :param text: Текст надписи
        :param row: Номер строки в окне
        """
        ttk.Label(self.frame_body, text=text, style='Regular.TLabel').grid(column=1, row=row, padx=5, pady=5)
        ttk.Button(
            self.frame_body, text='Загрузить', style='Regular.TButton',
            command=lambda: self.download_file(filename=text, root=root)
        ).grid(padx=10, pady=10, column=2, row=row)
        ttk.Button(
            self.frame_body, text='Предпросмотр', style='Regular.TButton',
            command=lambda: self.preview_file(filename=text, root=root)
        ).grid(padx=10, pady=10, column=3, row=row)
        ttk.Button(
            self.frame_body, text='Удалить вложение', style='Regular.TButton',
            width=20, command=lambda: self.delete_file(filename=text, root=root)
        ).grid(padx=10, pady=10, column=4, row=row)

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна ввода информации
        """
        ttk.Label(self.frame_header, text='Просмотр вложенных файлов', style='Title.TLabel').pack(side=TOP, pady=15)
        row_num = 1
        for root, dirs, files in os.walk(os.path.join('savings', 'attachments', self.mold_number)):
            for file in files:
                if os.path.join(root, file):
                    self.get_label_and_entry_widgets_in_row(text=file, row=row_num, root=root)
                    row_num += 1
        if row_num == 1:
            (ttk.Label(self.frame_body, text='Нет прикрпеплённых файлов', style='Regular.TLabel')
             .grid(column=1, row=row_num, padx=5, pady=5))
        # Запуск работы окна приложения
        self.mainloop()

    def download_file(self, filename: str, root: str):
        """
        Функция загрузки вложения (какого либо файла) в директорию выбранную пользователем
        :param part_number: ID номер элемента BOM относящегося к определённой пресс-форме
        :param hot_runner: Булево значение, которое характеризует какой тип BOM был выбран (Пресс-форма или горячий канал)
        """
        # Открытие диалогового окна для выбора пользователем локальной директории для сохранения файла,
        # c дальнейшим извлечением пути в виде строки
        try:
            local_file_path = filedialog.asksaveasfilename(
            # filetypes=(('XLSX files', '*.xlsx'),)
        )
        except AttributeError:
            pass
        else:
            try:
                shutil.copy2(os.path.join(root, filename), local_file_path)
            except IOError:
                messagebox.showerror(title='Ошибка',
                                     message='Файл не удалось загрузить. Обратитесь к администратору.')
            else:
                messagebox.showinfo(title='Уведомление', message='Файл успешно загружен')

    def open_additional_preview_window(self, filename: str, root: str):
        self.image = Image.open(os.path.join(root, filename)).resize((1024, 768))
        self.image_pil = ImageTk.PhotoImage(self.image)
        window = tkinter.Toplevel()
        window.title('Preview')
        window.geometry('1024x768')
        window.focus_set()
        (Label(window, image=self.image_pil)
         .pack(side=TOP, pady=5))

    def preview_file(self, filename: str, root: str):
        picture_type = None
        for filetype in ('.jpg' or '.jpeg' or '.png' or '.JPG' or '.JPEG'):
            if filetype in filename:
                picture_type = True
        if '.pdf' in filename:
            pages = convert_from_path(os.path.abspath(os.path.join('..', 'pics', filename)))
            for i in range(len(pages)):
                page_name = f'page{i}.jpg'
                pages[i].save(page_name, 'JPEG')
                self.open_additional_preview_window(page_name)
                os.remove(os.path.abspath(os.path.join('..', 'pics', page_name)))
        elif picture_type:
            self.open_additional_preview_window(filename, root)

    def delete_file(self, filename: str, root: str):
        if user_data.get('user_name'):
            if messagebox.askyesno(title='Подтверждение', message=f'Вы уверены, что хотите удалить файл {filename}?', parent=self):
                
                try:
                    os.remove(os.path.join(root, filename))
                except AttributeError:
                    messagebox.showerror(title='Ошибка',
                                     message='Файл не удалось загрузить. Обратитесь к администратору.')
                else:
                    messagebox.showinfo(title='Уведомление', message='Файл успешно удалён')
                    self.destroy()
                    attachments =  Attachment(self.mold_number, self.part_number, self.hot_runner)
                    attachments.render_widgets()
        else:
            messagebox.showerror('Ошибка',
                     'У Вас нет доступа. Для его предоставления обратитесь к администратору')
