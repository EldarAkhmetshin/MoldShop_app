#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import os
import re
import shutil
import tkinter
from os.path import abspath
from tkinter import *
from tkinter import messagebox, ttk, filedialog
from tkinter.ttk import Frame
from typing import Callable
from tkhtmlview import HTMLLabel

from src.data import error_messages
from src.global_values import user_data
from src.utils.logger.logs import get_info_log, get_warning_log


def download_file(filename: str, root: str):
    """
    Функция загрузки вложения (какого либо файла) в директорию, выбранную пользователем
    :param root: Путь к файлу
    :param filename: Имя файла
    """
    filetype = re.search(r'\.\w+', filename).group(0)
    # Открытие диалогового окна для выбора пользователем локальной директории для сохранения файла,
    # с дальнейшим извлечением пути в виде строки
    local_file_path = filedialog.asksaveasfilename(
        filetypes=((f'{filetype.upper()} files', f'*{filetype}'),)
    )

    if local_file_path:
        try:
            shutil.copy2(os.path.join(root, filename), f'{local_file_path}{filetype}')
        except IOError:
            get_warning_log(user=user_data.get('user_name'), message='IOError. Attachment was NOT uploaded',
                            func_name=download_file.__name__,
                            func_path=abspath(__file__))
        else:
            messagebox.showinfo(title='Уведомление', message='Файл успешно загружен')
            get_info_log(user=user_data.get('user_name'), message='Attachment was successfully uploaded',
                         func_name=download_file.__name__,
                         func_path=abspath(__file__))


class Attachment(tkinter.Toplevel):
    """
    Класс представляет набор функций для создания графического интерфейса дополнительного окна просмотра вложенных файлов, 
    редактирования, их предпросмотра и скачивания в указанную директорию пользователем
    """

    def __init__(self, mold_number: str, part_number: str = None, hot_runner: bool = None, checking: bool = None):
        """
        Создание переменных
        """
        self.scroll_y = None
        self.canvas = None
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
        self.folder_path = None
        if not checking:
            super().__init__()
            self.init_gui()

    def init_gui(self):
        """
        Инициация окна приложения и контейнера для размещения виджетов
        """
        self.focus_set()
        self.geometry('850x400')
        self.frame_header = Frame(self)
        self.frame_header.pack(fill=BOTH, expand=True)
        # создание канвас для прикрепления к нему прокрутки / скроллинга
        self.canvas = Canvas(self)
        self.frame_body = Frame(self.canvas)
        self.frame_body.pack(fill=BOTH, expand=True)
        self.scroll_y = tkinter.Scrollbar(self, orient=tkinter.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scroll_y.set)
        self.scroll_y.pack(side=RIGHT, fill='y')
        self.canvas.pack(fill=BOTH, expand=True)
        self.canvas.create_window((4, 4), window=self.frame_body, anchor="nw")

    def define_folder_path(self):
        """
        Функция определения пути к папке с прикрепленными файлами
        """
        if self.part_number:
            define_path: Callable = lambda: os.path.join('savings', 'attachments', self.mold_number, 'hot_runner_parts',
                                                         str(self.part_number)) \
                if self.hot_runner else os.path.join('savings', 'attachments', self.mold_number, 'mold_parts',
                                                     str(self.part_number))
            self.folder_path = define_path()
        else:
            self.folder_path = os.path.join('savings', 'attachments', str(self.mold_number))

    def get_label_and_entry_widgets_in_row(self, text: str, row: int, root: str):
        """
        Рендер виджетов окна расположенных в одной строке
        :param root: Путь к файлу
        :param text: Текст надписи
        :param row: Номер строки в окне
        """
        sub_frame = Frame(self.frame_body)
        sub_frame.pack(fill=BOTH, expand=True)
        HTMLLabel(sub_frame, html=f"""
                                <a href="{os.path.abspath(os.path.join(root, text))}">{text}</a>
                                """, width=60, height=2).grid(padx=10, pady=10, column=1, row=row)
        ttk.Button(
            sub_frame, text='Загрузить', style='Regular.TButton', width=10,
            command=lambda: download_file(filename=text, root=root)
        ).grid(padx=10, pady=10, column=2, row=row)
        ttk.Button(
            sub_frame, text='Удалить вложение', style='Regular.TButton',
            width=20, command=lambda: self.delete_file(filename=text, root=root)
        ).grid(padx=10, pady=10, column=3, row=row)

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна ввода информации
        """
        self.define_folder_path()

        ttk.Label(self.frame_header, text='Просмотр вложенных файлов '
                                          f'для {self.part_number if self.part_number else self.mold_number}',
                  style='Title.TLabel').pack(side=TOP, pady=15)
        row_num = 1
        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if os.path.join(root, file):
                    self.get_label_and_entry_widgets_in_row(text=file, row=row_num, root=root)
                    row_num += 1
        if row_num == 1:
            (ttk.Label(self.frame_body, text='Нет прикреплённых файлов', style='Regular.TLabel')
             .grid(column=1, row=row_num, padx=5, pady=5))
        # Обновление размеров канваса после добавления всех виджетов в него
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # Запуск работы окна приложения
        get_info_log(user=user_data.get('user_name'), message='Attachments window was rendered',
                     func_name=self.render_widgets.__name__,
                     func_path=abspath(__file__))
        self.mainloop()

    def search_attachments(self) -> bool:
        """
        Функция проверки на наличие прикреплённых файлов к элементу BOM или к пресс-форме
        :return: Булево значение характеризующее результат поиска
        """
        self.define_folder_path()

        for root, dirs, files in os.walk(self.folder_path):
            for file in files:
                if os.path.join(root, file):
                    return True

        return False

    def delete_file(self, filename: str, root: str):
        """
        Функция для удаления вложенного файла
        :param root: Путь к файлу
        :param filename: Имя файла
        """
        if user_data.get('attachments_changing') == 'True':
            if messagebox.askyesno(title='Подтверждение', message=f'Вы уверены, что хотите удалить файл {filename}?',
                                   parent=self):

                try:
                    os.remove(os.path.join(root, filename))
                except AttributeError:
                    messagebox.showerror(title='Ошибка',
                                         message='Файл не удалось удалить. Обратитесь к администратору.')
                    get_warning_log(user=user_data.get('user_name'), message='Attachment file was NOT deleted',
                                    func_name=self.delete_file.__name__,
                                    func_path=abspath(__file__))
                else:
                    messagebox.showinfo(title='Уведомление', message='Файл успешно удалён')
                    self.destroy()
                    attachments = Attachment(self.mold_number, self.part_number, self.hot_runner)
                    attachments.render_widgets()
                    get_info_log(user=user_data.get('user_name'), message='Attachment file was successfully deleted',
                                 func_name=self.delete_file.__name__,
                                 func_path=abspath(__file__))
        else:
            messagebox.showerror(error_messages.get('access_denied').get('message_name'),
                                 error_messages.get('access_denied').get('message_body'))
