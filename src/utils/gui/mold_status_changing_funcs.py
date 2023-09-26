#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import sqlite3
import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Frame
from typing import Callable
from datetime import datetime

from src.config_data.config import passwords
from src.global_values import user_data
from src.utils.sql_database import table_funcs


class QRWindow(tkinter.Toplevel):
    """
    Класс представляет набор функций для создания графического интерфейса окна получения сообщения от сканера после сканерования QR кода на пресс-форме для изменения её статуса.
    Также включены функции обработки полученной ин
    """

    def __init__(self, next_status: str):
        """
        Создание переменных
        """
        self.next_status = next_status
        self.tracked_variable = StringVar()
        self.tracked_variable.trace("w", self.check_entry_field)
        self.code_entry_field = None
        self.changed_data = None
        self.input_error_label = None
        self.frame = None
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.confirm_delete)
        self.init_gui()

    def init_gui(self):
        """
        Инициация окна приложения и контейнера для размещения виджетов
        """
        self.focus_set()
        self.grab_set()
        self.frame = Frame(self)
        self.frame.pack()

    def check_entry_field(self, *args):
        """
        Проверка каждого введенного символа в поле ввода
        :param args:
        """
        text = self.tracked_variable.get()
        if ';' in text:
            self.tracked_variable.set("")
            self.validate_and_save_edited_data()

    def render_widgets_before_getting_code(self):
        """
        Функция рендера всех виджетов окна ввода информации
        """

        (Label(self.frame, text='Отсканнируйте QR код', font=('Times', '20', 'normal')).pack(side=TOP, pady=10))

        self.code_entry_field = Entry(self.frame, show='*', font=('Times', '25', 'normal'),
                                      textvariable=self.tracked_variable)
        self.code_entry_field.pack(side=TOP, pady=10, padx=10)
        self.code_entry_field.focus_set()

        # Button(
        #        self.frame, text='Применить', background='white',
        #        width=20, font=('Times', '10'),
        #        command=self.validate_and_save_new_part_data
        # ).grid(padx=10, pady=10, column=2, row=14)
        # Запуск работы окна приложения
        self.mainloop()

    def validate_and_save_edited_data(self):
        """
        Фнкция проверки введённых данных пользователем
        """
        # Проверка правильности ввода информации
        scanned_code = self.code_entry_field.get()
        if scanned_code:
            mold_number = scanned_code.replace('mold_', '').replace(';', '')
            # Загрузка изменённых данных в базу данных
            try:
                # Сохранение нового статус п/ф в таблице перечня пресс-форм
                molds_data = table_funcs.TableInDb('All_molds_data', 'Database')
                mold_info = molds_data.get_table(type_returned_data='dict', param='MOLD_NUMBER', value=mold_number,
                                                 last_string=True)
                molds_data.change_data(param='MOLD_NUMBER', value=mold_number,
                                       data={
                                           'STATUS': self.next_status,
                                       })
                # Запись в журнал
                moving_history = table_funcs.TableInDb('Molds_moving_history', 'Database')
                moving_history.insert_data(info=(str(datetime.now()), user_data.get('user_name'), mold_number,
                                                 mold_info.get('MOLD_NAME'), mold_info.get('STATUS'), self.next_status))
            except sqlite3.ProgrammingError:
                self.input_error_label = Label(self.frame,
                                               text='Ошибка записи данных! Обратитесь к администратору',
                                               foreground='Red')
                self.input_error_label.grid(column=1, row=12)
            else:
                self.quit()
                self.destroy()
                messagebox.showinfo('Уведомление', 'Информация о пресс-форме успешно изменена')
                self.changed_data = True
        else:
            # Если данные введены некорректно пользователь получит уведомление об ошибке
            self.input_error_label = Label(self.frame,
                                           text='Не заполненны обязательные поля', foreground='Red')
            self.input_error_label.grid(column=1, row=12)

    def confirm_delete(self):
        message = "Вы уверены, что хотите закрыть это окно?"
        if messagebox.askyesno(message=message, parent=self):
            self.destroy()