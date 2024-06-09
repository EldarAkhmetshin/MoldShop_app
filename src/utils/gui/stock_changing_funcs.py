#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import sqlite3
import tkinter
from dataclasses import dataclass
from datetime import datetime
from os.path import abspath
from tkinter import *
from tkinter import messagebox, ttk
from tkinter.ttk import Frame
from typing import Callable

from src.data import DB_NAME
from src.global_values import user_data
from src.utils.logger.logs import get_info_log, get_warning_log
from src.utils.sql_database import table_funcs


@dataclass
class Stock(tkinter.Toplevel):
    """
    Класс представляет набор функций для создания графического интерфейса окна изменения количества какого либо
    элемента на складе.
    """
    mold_number: str
    part_data: dict
    table_name: str
    consumption: bool = None
    parts_quantity_entry_field: tkinter.Entry = None
    used_parts_quantity_entry_field: tkinter.Entry = None
    required_part_type: str = None
    quantity_entry_field: tkinter.Entry = None
    part_type_combobox: ttk.Combobox = None
    required_quantity: str | int = None
    changed_data: bool = None
    input_error_label: tkinter.Label = None

    def __post_init__(self):
        """
        Инициация контейнеров для размещения виджетов и некоторых переменнных
        """
        super().__init__()
        self.focus_set()
        self.grab_set()
        self.frame_header: tkinter.Frame = Frame(self)
        self.frame_header.pack()
        self.frame_body: tkinter.Frame = Frame(self)
        self.frame_body.pack()
        self.frame_bottom: tkinter.Frame = Frame(self)
        self.frame_bottom.pack()

        self.part_number: str = self.part_data.get('NUMBER')
        self.part_name: str = self.part_data.get('PART_NAME')
        self.parts_quantity: int = int(self.part_data.get('PARTS_QUANTITY')) \
            if self.part_data.get('PARTS_QUANTITY') else 0
        self.used_parts_quantity: int = int(self.part_data.get('USED_PARTS_QUANTITY')) \
            if self.part_data.get('USED_PARTS_QUANTITY') else 0
        self.storage_cell: str = self.part_data.get('STORAGE_CELL')

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна ввода информации
        """
        define_title: Callable = lambda: 'Списание запчастей' if self.consumption else 'Приход запчастей'

        ttk.Label(self.frame_header, text=define_title(), style='Title.TLabel').pack(side=TOP, pady=15)

        ttk.Label(self.frame_body, text='Тип запчасти', style='Regular.TLabel').grid(column=1, row=1, padx=5, pady=5)
        self.part_type_combobox = ttk.Combobox(self.frame_body, values=['Новая', 'Б/У'], state='readonly')
        self.part_type_combobox.grid(column=2, row=1, padx=5, pady=5)

        ttk.Label(self.frame_body, text='Количество', style='Regular.TLabel').grid(column=1, row=2, padx=5, pady=5)
        self.quantity_entry_field = ttk.Entry(self.frame_body, font=('Times', '11', 'normal'))
        self.quantity_entry_field.grid(column=2, row=2, padx=5, pady=5)

        ttk.Button(
            self.frame_bottom, text='Применить', style='Regular.TButton',
            command=self.validate_and_save_changed_data
        ).pack(padx=10, pady=10, side=TOP)
        # Запуск работы окна приложения
        get_info_log(user=user_data.get('user_name'), message='Stock changing window was rendered',
                     func_name=self.render_widgets.__name__, func_path=abspath(__file__))

        self.mainloop()

    def define_column_name(self) -> str:
        """
        Функция определения типа запрашиваемой запчасти / BOM элемента
        :return: Соответствующий тип запчасти
        """
        return 'PARTS_QUANTITY' if self.consumption else 'USED_PARTS_QUANTITY'

    def get_end_quantity(self) -> int:
        """
        Функция для получения конечного остатка на складе выбранного элемента из BOM в результате прихода или расхода
        :return: Оставшееся количество выбранного элемента
        """
        define_income_quantity: Callable = lambda: self.parts_quantity \
            if self.required_part_type == 'Новая' else self.used_parts_quantity

        return define_income_quantity() - self.required_quantity if self.consumption else define_income_quantity() + self.required_quantity

    def check_parts_quantity(self) -> bool:
        """
        Функция проверки введенного значения пользователем и проверки возможности выдачи запрашиваемого
        кол-ва пользователю
        :return: True если запрос корректен
        """
        define_income_quantity: Callable = lambda: self.parts_quantity \
            if self.required_part_type == 'Новая' else self.used_parts_quantity
        try:
            self.required_quantity = int(self.required_quantity)
        except ValueError:
            self.input_error_label = Label(self.frame_bottom,
                                           text='В поле количество введите число',
                                           foreground='Red')
        else:
            if self.consumption and self.required_quantity > define_income_quantity():
                self.input_error_label = Label(self.frame_bottom,
                                               text='Запрашиваемое количество отсутствует на складе. Введите другое '
                                                    'число.',
                                               foreground='Red')
            else:
                return True

    def validate_and_save_changed_data(self):
        """
        Функция проверки введённых данных пользователем
        """
        # Определения столбца для изменения данных
        define_column_name: Callable = lambda: 'PARTS_QUANTITY' \
            if self.required_part_type == 'Новая' else 'USED_PARTS_QUANTITY'
        # Определение имени таблицы для сохранения истории изменений склада
        define_table_name: Callable = lambda: 'OUT_warehouse_history' if self.consumption else 'IN_warehouse_history'
        # Определение данных для записи в таблицу с историей изменений склада
        define_data: Callable = lambda: (
            str(datetime.now().strftime("%m/%d/%Y, %H:%M")), user_data.get('user_name'), self.mold_number,
            self.part_number, self.part_name, self.required_part_type, self.required_quantity)
        if self.input_error_label:
            self.input_error_label.destroy()

        self.required_part_type = self.part_type_combobox.get()
        self.required_quantity = self.quantity_entry_field.get()
        # Проверка на заполнение обязательных полей
        if self.required_part_type and self.required_quantity:
            if self.check_parts_quantity():
                # Загрузка данных в базу данных
                try:
                    # Изменение количества запчастей в BOM
                    bom = table_funcs.TableInDb(self.table_name, DB_NAME)
                    bom.change_data(first_param='NUMBER', first_value=self.part_number,
                                    data={define_column_name(): self.get_end_quantity()}, second_param='PART_NAME',
                                    second_value=self.part_name)
                    # Новая запись в журнале истории изменений склада
                    warehouse_history = table_funcs.TableInDb(define_table_name(), DB_NAME)
                    warehouse_history.insert_data(info=define_data())
                except sqlite3.ProgrammingError:
                    self.input_error_label = Label(self.frame_bottom,
                                                   text='Ошибка записи данных! Обратитесь к администратору',
                                                   foreground='Red')
                    self.input_error_label.grid(column=1, row=12)
                    get_warning_log(user=user_data.get('user_name'),
                                    message='SqliteProgrammingError. Part cnt wasnt changed',
                                    func_name=self.validate_and_save_changed_data.__name__, func_path=abspath(__file__))
                else:
                    self.quit()
                    self.destroy()
                    messagebox.showinfo('Уведомление',
                                        f'Итоговое количество успешно изменено.'
                                        f'\nЯчейка хранения: {self.storage_cell}')
                    self.changed_data = True
                    get_info_log(user=user_data.get('user_name'), message='Part cnt was changed',
                                 func_name=self.validate_and_save_changed_data.__name__, func_path=abspath(__file__))
            else:
                self.input_error_label.pack(side=TOP, padx=5, pady=5)
                get_warning_log(user=user_data.get('user_name'),
                                message='Required part cnt wasnt correct. Part cnt wasnt changed',
                                func_name=self.validate_and_save_changed_data.__name__, func_path=abspath(__file__))
        # Если данные введены некорректно пользователь получит уведомление об ошибке
        else:
            self.input_error_label = Label(self.frame_bottom,
                                           text='Не выбран тип запчасти', foreground='Red')
            self.input_error_label.pack(side=TOP, padx=5, pady=5)
            get_warning_log(user=user_data.get('user_name'),
                            message='Part type wasnt selected. Part cnt wasnt changed',
                            func_name=self.validate_and_save_changed_data.__name__, func_path=abspath(__file__))
