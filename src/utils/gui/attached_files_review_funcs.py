#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import os
import re
import shutil
import tkinter
from tkinter import *
from tkinter import messagebox, ttk, filedialog
from tkinter.ttk import Frame
from typing import Callable
from PIL import ImageTk, Image
from pdf2image import convert_from_path
from tkhtmlview import HTMLLabel

from src.data import error_messages
from src.global_values import user_data


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
        :param root: Путь к файлу
        :param text: Текст надписи
        :param row: Номер строки в окне
        """
        HTMLLabel(self.frame_body, html=f"""
                                <a href="{os.path.abspath(os.path.join(root, text))}">{text}</a>
                                """, width=60, height=2).grid(padx=10, pady=10, column=1, row=row)
        # ttk.Label(self.frame_body, text=text, style='Regular.TLabel').grid(column=1, row=row, padx=5, pady=5)
        ttk.Button(
            self.frame_body, text='Загрузить', style='Regular.TButton', width=10,
            command=lambda: self.download_file(filename=text, root=root)
        ).grid(padx=10, pady=10, column=2, row=row)
        # ttk.Button(
        #     self.frame_body, text='Предпросмотр', style='Regular.TButton',
        #     command=lambda: self.preview_file(filename=text, root=root)
        # ).grid(padx=10, pady=10, column=3, row=row)
        ttk.Button(
            self.frame_body, text='Удалить вложение', style='Regular.TButton',
            width=20, command=lambda: self.delete_file(filename=text, root=root)
        ).grid(padx=10, pady=10, column=3, row=row)
        # HTMLLabel(self.frame_body, html=f"""
        #                         <a href="{os.path.abspath(os.path.join(root, text))}">Просмотр</a>
        #                         """, width=15, height=2).grid(padx=10, pady=10, column=4, row=row)

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна ввода информации
        """
        if self.part_number:
            define_path: Callable = lambda: os.path.join('savings', 'attachments', self.mold_number, 'hot_runner_parts',
                                                         self.part_number) \
                if self.hot_runner else os.path.join('savings', 'attachments', self.mold_number, 'mold_parts',
                                                     self.part_number)
            path = define_path()
        else:
            path = os.path.join('savings', 'attachments', self.mold_number)

        ttk.Label(self.frame_header, text='Просмотр вложенных файлов', style='Title.TLabel').pack(side=TOP, pady=15)
        row_num = 1
        for root, dirs, files in os.walk(path):
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
        :param root: Путь к файлу
        :param filename: Имя файла
        """
        filetype = re.search(r'\.\w+', filename).group(0)
        # Открытие диалогового окна для выбора пользователем локальной директории для сохранения файла,
        # c дальнейшим извлечением пути в виде строки

        local_file_path = filedialog.asksaveasfilename(
            filetypes=((f'{filetype.upper()} files', f'*{filetype}'),)
        )
        if local_file_path:
            try:
                shutil.copy2(os.path.join(root, filename), f'{local_file_path}{filetype}')
            except IOError:
                pass
            else:
                messagebox.showinfo(title='Уведомление', message='Файл успешно загружен')

    def open_additional_preview_window(self, filename: str, root: str):
        """
        Функция  для рендера доп. окна предпросмотра выбранного изображения
        :param root: Путь к файлу
        :param filename: Имя файла
        """
        self.image = Image.open(os.path.join(root, filename)).resize((1024, 768))
        self.image_pil = ImageTk.PhotoImage(self.image)
        window = tkinter.Toplevel()
        window.iconbitmap(os.path.join('pics', 'artpack.ico'))
        window.title('Preview')
        window.geometry('1024x768')
        window.focus_set()
        (Label(window, image=self.image_pil)
         .pack(side=TOP, pady=5))

    def preview_file(self, filename: str, root: str):
        """
        Функция проверки возможности предпросмотра изображений / PDF файлов и вызова функции для рендера доп. окна 
        :param root: Путь к файлу
        :param filename: Имя файла
        """
        picture_type = None
        for filetype in ('.jpg' or '.jpeg' or '.png' or '.JPG' or '.JPEG'):
            if filetype in filename:
                picture_type = True
        if '.pdf' in filename:
            pages = convert_from_path(os.path.abspath(os.path.join(root, filename)))
            for i in range(len(pages)):
                page_name = f'page{i}.jpg'
                pages[i].save(page_name, 'JPEG')
                self.open_additional_preview_window(page_name, root)
                os.remove(os.path.abspath(os.path.join(root, page_name)))
        elif picture_type:
            self.open_additional_preview_window(filename, root)

    def delete_file(self, filename: str, root: str):
        """
        Функция  для удаления вложенного файла
        :param root: Путь к файлу
        :param filename: Имя файла
        """
        if user_data.get('attachments_changing'):
            if messagebox.askyesno(title='Подтверждение', message=f'Вы уверены, что хотите удалить файл {filename}?', parent=self):

                try:
                    os.remove(os.path.join(root, filename))
                except AttributeError:
                    messagebox.showerror(title='Ошибка',
                                         message='Файл не удалось загрузить. Обратитесь к администратору.')
                else:
                    messagebox.showinfo(title='Уведомление', message='Файл успешно удалён')
                    self.destroy()
                    attachments = Attachment(self.mold_number, self.part_number, self.hot_runner)
                    attachments.render_widgets()
        else:
            messagebox.showerror(error_messages.get('access_denied').get('message_name'),
                                 error_messages.get('access_denied').get('message_body'))
