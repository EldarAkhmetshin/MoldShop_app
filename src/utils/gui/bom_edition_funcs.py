#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import os
import sqlite3
import tkinter
from os.path import abspath
from tkinter import *
from tkinter import messagebox, ttk
from tkinter.ttk import Frame
from typing import Callable

from src.global_values import user_data
from src.utils.logger.logs import get_info_log, get_warning_log
from src.utils.sql_database import table_funcs


class EditedBOM(tkinter.Toplevel):
    """
    Класс представляет набор функций для создания графического интерфейса окон редактирования
    информации о выбранной запчасти из BOM пресс-формы, а также валидации и записи новой информации
    в таблицы базы данных.
    """

    def __init__(self, mold_number: str, table_name: str, part_data: dict = None):
        """
        Создание переменных
        """
        self.frame_bottom = None
        self.frame_body = None
        self.frame_header = None
        if part_data is None:
            self.part_data = {}
        else:
            self.part_data = part_data
        self.table_name = table_name
        self.mold_number = mold_number
        self.min_percent_entry_field = None
        self.storage_cell_entry_field = None
        self.used_parts_quantity_entry_field = None
        self.parts_quantity_entry_field = None
        self.dimensions_entry_field = None
        self.material_entry_field = None
        self.supplier_entry_field = None
        self.additional_info_entry_field = None
        self.description_entry_field = None
        self.pcs_in_mold_entry_field = None
        self.name_entry_field = None
        self.number_entry_field = None
        self.number = self.part_data.get('NUMBER')
        self.part_name = self.part_data.get('PART_NAME')
        self.pcs_in_mold = self.part_data.get('PCS_IN_MOLDS')
        self.description = self.part_data.get('DESCRIPTION')
        self.additional_info = self.part_data.get('ADDITIONAL_INFO')
        self.supplier = self.part_data.get('SUPPLIER')
        self.material = self.part_data.get('MATERIAL')
        self.dimensions = self.part_data.get('DIMENSIONS')
        self.storage_cell = self.part_data.get('STORAGE_CELL')
        self.min_percent = self.part_data.get('MIN_PERCENT')

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
        self.frame_header = Frame(self)
        self.frame_header.pack(fill=BOTH, expand=True)
        self.frame_body = Frame(self)
        self.frame_body.pack(fill=BOTH, expand=True)
        self.frame_bottom = Frame(self)
        self.frame_bottom.pack(fill=BOTH, expand=True)

    def get_label_and_entry_widgets_in_row(self, text: str, point_info: str, row: int,
                                           necessary_field: bool = None) -> tkinter.Entry:
        """
        Рендер виджетов окна расположенных в одной строке
        :param text: Текст надписи
        :param point_info: Текущее значение (до изменения)
        :param row: Номер строки в окне
        :param necessary_field: Булево значение о необходимости заполнения данных
        :return: Виджет поля ввода
        """
        ttk.Label(self.frame_body, text=text, style='Regular.TLabel').grid(column=1, row=row, padx=5, pady=5)
        if self.part_data:
            entry_column_num = 3
            ttk.Label(self.frame_body, text=point_info, style='Regular.TLabel').grid(column=2, row=row, padx=5, pady=5)
        else:
            entry_column_num = 2

        if necessary_field and not self.part_data:
            ttk.Label(self.frame_body, text='*', font=('Times', '13')).grid(column=4, row=row)
        entry_field = ttk.Entry(self.frame_body, font=('Times', '10', 'bold'))
        entry_field.grid(pady=5, padx=2, column=entry_column_num, row=row)
        return entry_field

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна ввода информации
        """
        define_title: Callable = lambda: 'Редактирование информации о запчасти' \
            if self.part_data else 'Добавление нового элемента в BOM'
        define_command: Callable = lambda: self.validate_and_save_edited_part_data() if self.part_data \
            else self.validate_and_save_new_part_data()

        ttk.Label(self.frame_header, text=define_title(), style='Title.TLabel').pack(side=TOP, pady=15)

        self.number_entry_field = self.get_label_and_entry_widgets_in_row(text='Номер', point_info=self.number,
                                                                          row=2, necessary_field=True)
        self.name_entry_field = self.get_label_and_entry_widgets_in_row(text='Наименование',
                                                                        point_info=self.part_name, necessary_field=True,
                                                                        row=3)
        self.pcs_in_mold_entry_field = self.get_label_and_entry_widgets_in_row(text='Кол-во в п/ф',
                                                                               point_info=self.pcs_in_mold, row=4)
        self.description_entry_field = self.get_label_and_entry_widgets_in_row(text='Описание',
                                                                               point_info=self.description, row=5)
        self.additional_info_entry_field = self.get_label_and_entry_widgets_in_row(text='Дополнительная информация',
                                                                                   point_info=self.additional_info,
                                                                                   row=6)
        self.supplier_entry_field = self.get_label_and_entry_widgets_in_row(text='Поставщик',
                                                                            point_info=self.supplier, row=7)
        self.material_entry_field = self.get_label_and_entry_widgets_in_row(text='Материал',
                                                                            point_info=self.material, row=8)
        self.dimensions_entry_field = self.get_label_and_entry_widgets_in_row(text='Габаритные размеры',
                                                                              point_info=self.dimensions, row=9)
        self.storage_cell_entry_field = self.get_label_and_entry_widgets_in_row(text='Ячейка хранения',
                                                                                point_info=self.storage_cell, row=12)
        self.min_percent_entry_field = self.get_label_and_entry_widgets_in_row(text='Необходимый минимум, %',
                                                                               point_info=self.min_percent,
                                                                               row=13)

        ttk.Button(
            self.frame_bottom, text='Применить', style='Regular.TButton',
            width=20,
            command=define_command
        ).pack(side=TOP, padx=10, pady=10)
        get_info_log(user=user_data.get('user_name'), message='Bom edition win was rendered',
                     func_name=self.render_widgets.__name__, func_path=abspath(__file__))
        # Запуск работы окна приложения
        self.mainloop()

    def change_paths(self, new_part_number: str):
        """
        Функция переименования папок для хранения прикреплённых файлов к элементу открытого BOM в случае
        изменения номера элемента
        :param new_part_number: Новый номер элемента
        """
        try:
            os.rename(os.path.join('savings', 'attachments', self.mold_number, 'mold_parts', self.number),
                      os.path.join('savings', 'attachments', self.mold_number, 'mold_parts', new_part_number))
        except FileNotFoundError:
            pass
        try:
            os.rename(os.path.join('savings', 'attachments', self.mold_number, 'hot_runner_parts', self.number),
                      os.path.join('savings', 'attachments', self.mold_number, 'hot_runner_parts', new_part_number))
        except FileNotFoundError:
            pass

    def validate_and_save_new_part_data(self):
        """
        Функция проверки введённых данных пользователем
        """
        if self.input_error_label:
            self.input_error_label.destroy()
        # Проверка на заполнение обязательных полей
        part_number = self.number_entry_field.get()
        part_name = self.name_entry_field.get()
        if part_number and part_name:
            # Загрузка данных в базу данных
            row = (
                part_number, part_name, self.pcs_in_mold_entry_field.get(), self.description_entry_field.get(),
                self.additional_info_entry_field.get(), self.supplier_entry_field.get(),
                self.material_entry_field.get(), self.dimensions_entry_field.get(),
                self.parts_quantity_entry_field.get(), self.used_parts_quantity_entry_field.get(),
                self.storage_cell_entry_field.get(), self.min_percent_entry_field.get()
            )
            try:
                bom = table_funcs.TableInDb(self.table_name, 'Database')
                bom.insert_data(info=row)
            except sqlite3.ProgrammingError:
                self.input_error_label = Label(self.frame,
                                               text='Ошибка записи данных! Обратитесь к администратору',
                                               foreground='Red')
                self.input_error_label.grid(column=1, row=15)
                get_warning_log(user=user_data.get('user_name'), message='New bom data was NOT added',
                                func_name=self.validate_and_save_new_part_data.__name__, func_path=abspath(__file__))
            else:
                self.quit()
                self.destroy()
                messagebox.showinfo('Уведомление',
                                    'Информация о новом элементе успешно добавлена в BOM')
                self.changed_data = True
                get_info_log(user=user_data.get('user_name'), message='New BOM data was successfully added',
                             func_name=self.validate_and_save_new_part_data.__name__, func_path=abspath(__file__))
        # Если данные введены некорректно пользователь получит уведомление об ошибке
        else:
            self.input_error_label = Label(self.frame,
                                           text='Не заполнены обязательные поля', foreground='Red')
            self.input_error_label.grid(column=1, row=15)

    def validate_and_save_edited_part_data(self):
        """
        Функция проверки введённых данных пользователем
        """
        # Проверка правильности ввода информации
        if self.input_error_label:
            self.input_error_label.destroy()
        try:
            pass
        except ValueError:
            self.input_error_label = Label(self.frame,
                                           text='В графах "Год выпуска" и "Количество гнёзд" '
                                                'должны быть числовые значения',
                                           foreground='Red')
            self.input_error_label.grid(column=1, row=12)
        else:
            # Загрузка изменённых данных в базу данных
            try:
                define_data: Callable = lambda old_data, new_data: new_data if new_data else old_data
                bom = table_funcs.TableInDb(self.table_name, 'Database')
                bom.change_data(first_param='NUMBER', first_value=self.number,
                                data={
                                    'NUMBER': define_data(old_data=self.number,
                                                          new_data=self.number_entry_field.get()),
                                    'PART_NAME': define_data(old_data=self.part_name,
                                                             new_data=self.name_entry_field.get()),
                                    'PCS_IN_MOLDS': define_data(old_data=self.pcs_in_mold,
                                                                new_data=self.pcs_in_mold_entry_field.get()),
                                    'DESCRIPTION': define_data(old_data=self.description,
                                                               new_data=self.description_entry_field.get()),
                                    'ADDITIONAL_INFO': define_data(old_data=self.additional_info,
                                                                   new_data=self.additional_info_entry_field.get()),
                                    'SUPPLIER': define_data(old_data=self.supplier,
                                                            new_data=self.supplier_entry_field.get()),
                                    'MATERIAL': define_data(old_data=self.material,
                                                            new_data=self.material_entry_field.get()),
                                    'DIMENSIONS': define_data(old_data=self.dimensions,
                                                              new_data=self.dimensions_entry_field.get()),
                                    'STORAGE_CELL': define_data(old_data=self.storage_cell,
                                                                new_data=self.storage_cell_entry_field.get()),
                                    'MIN_PERCENT': define_data(old_data=self.min_percent,
                                                               new_data=self.min_percent_entry_field.get())
                                })
                new_part_number = self.number_entry_field.get()
                if new_part_number:
                    self.change_paths(new_part_number)
            except (sqlite3.ProgrammingError, sqlite3.OperationalError):
                self.input_error_label = Label(self.frame,
                                               text='Ошибка записи данных! Обратитесь к администратору',
                                               foreground='Red')
                self.input_error_label.grid(column=1, row=12)
                get_warning_log(user=user_data.get('user_name'), message='Bom data was NOT changed',
                                func_name=self.validate_and_save_edited_part_data.__name__, func_path=abspath(__file__))
            else:
                self.quit()
                self.destroy()
                messagebox.showinfo('Уведомление', 'Информация о пресс-форме успешно изменена')
                self.changed_data = True
                get_info_log(user=user_data.get('user_name'), message='Bom data was successfully changed',
                             func_name=self.validate_and_save_edited_part_data.__name__, func_path=abspath(__file__))

    def confirm_delete(self):
        """
        Функция вывода диалогового окна для запроса подтверждения закрытия окна
        """
        message = "Вы уверены, что хотите закрыть это окно?"
        if messagebox.askyesno(message=message, parent=self):
            self.destroy()
