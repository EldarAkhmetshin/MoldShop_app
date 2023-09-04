#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import sqlite3
import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Frame
from typing import Callable

from src.config_data.config import passwords
from src.global_values import user_data
from src.utils.sql_database import table_funcs


class EditedBOM(tkinter.Toplevel):
    """
    Класс представляет набор функций для создания графического интерфейса окна редактирования
    информации о выбранной запчасти из BOM пресс-формы.
    """

    def __init__(self, part_data: dict, mold_number: str):
        """
        Создание переменных
        """
        self.mold_number = mold_number
        self.min_percent_entry_field = None
        self.storage_cell_entry_field = None
        self.used_parts_quantity_entry_field = None
        self.parts_qantity_entry_field = None
        self.dimensions_entry_field = None
        self.material_entry_field = None
        self.supplier_entry_field = None
        self.additional_info_entry_field = None
        self.description_entry_field = None
        self.pcs_in_mold_entry_field = None
        self.name_entry_field = None
        self.number_entry_field = None
        self.number = part_data.get('NUMBER')
        self.part_name = part_data.get('PART_NAME')
        self.pcs_in_mold = part_data.get('PCS_IN_MOLDS')
        self.description = part_data.get('DESCRIPTION')
        self.additional_info = part_data.get('ADDITIONAL_INFO')
        self.supplier = part_data.get('SUPPLIER')
        self.material = part_data.get('MATERIAL')
        self.dimensions = part_data.get('DIMENSIONS')
        self.parts_quantity = part_data.get('PARTS_QUANTITY')
        self.used_parts_quantity = part_data.get('USED_PARTS_QUANTITY')
        self.storage_cell = part_data.get('STORAGE_CELL')
        self.min_percent = part_data.get('MIN_PERCENT')

        self.edited_part_data = None
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
        Label(self.frame, text=text).grid(column=1, row=row, padx=5, pady=5)
        Label(self.frame, text=point_info).grid(column=2, row=row, padx=5, pady=5)

        if necessary_field:
            Label(self.frame, text='*', font=('Times', '13')).grid(column=4, row=row)
        entry_field = Entry(self.frame, font=('Times', '10', 'bold'))
        entry_field.grid(pady=5, column=3, row=row)
        return entry_field

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна ввода информации о новой пресс-форме
        """
        (Label(self.frame, text='Редактирование информации о запчасти', font=('Times', '15', 'bold'))
         .grid(column=2, row=1, pady=15))

        self.number_entry_field = self.get_label_and_entry_widgets_in_row(text='Номер', point_info=self.number,
                                                                          row=2, necessary_field=True)
        self.name_entry_field = self.get_label_and_entry_widgets_in_row(text='Наименование',
                                                                        point_info=self.part_name, row=3)
        self.pcs_in_mold_entry_field = self.get_label_and_entry_widgets_in_row(text='Кол-во в п/ф',
                                                                               point_info=self.pcs_in_mold,
                                                                               row=4, necessary_field=True)
        self.description_entry_field = self.get_label_and_entry_widgets_in_row(text='Описание',
                                                                               point_info=self.description,
                                                                               row=5, necessary_field=True)
        self.additional_info_entry_field = self.get_label_and_entry_widgets_in_row(text='Дополнительная информация',
                                                                                   point_info=self.additional_info,
                                                                                   row=6, necessary_field=True)
        self.supplier_entry_field = self.get_label_and_entry_widgets_in_row(text='Поставщик',
                                                                            point_info=self.supplier,
                                                                            row=7, necessary_field=True)
        self.material_entry_field = self.get_label_and_entry_widgets_in_row(text='Материал',
                                                                            point_info=self.material,
                                                                            row=8, necessary_field=True)
        self.dimensions_entry_field = self.get_label_and_entry_widgets_in_row(text='Габаритные размеры',
                                                                              point_info=self.dimensions,
                                                                              row=9)
        self.parts_qantity_entry_field = self.get_label_and_entry_widgets_in_row(text='Остаток', row=10,
                                                                                 point_info=self.parts_quantity,
                                                                                 necessary_field=True)
        self.used_parts_quantity_entry_field = self.get_label_and_entry_widgets_in_row(text='Остаток б/у',
                                                                                       point_info=self.used_parts_quantity,
                                                                                       row=11)
        self.storage_cell_entry_field = self.get_label_and_entry_widgets_in_row(text='Ячейка хранения',
                                                                                point_info=self.storage_cell, row=12)
        self.min_percent_entry_field = self.get_label_and_entry_widgets_in_row(text='Необходимый минимум, %',
                                                                               point_info=self.used_parts_quantity,
                                                                               row=13)

        Button(
            self.frame, text='Применить', background='white',
            width=20, font=('Times', '10'),
            command=self.validate_and_save_edited_mold_data
        ).grid(padx=10, pady=10, column=2, row=14)
        # Запуск работы окна приложения
        self.mainloop()

    def validate_and_save_edited_mold_data(self):
        """
        Фнкция проверки введённых данных пользователем
        """
        # Проверка правильности ввода информации о годе выпуска пресс формы и количестве гнёзд
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
                molds_data = table_funcs.TableInDb(f'BOM_{self.mold_number}', 'Database')
                molds_data.change_few_data(param='NUMBER', value=self.number,
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
                                               # 'PARTS_QUANTITY': define_data(old_data=self.parts_quantity,
                                               #                       new_data=self.parts_qantity_entry_field.get()),
                                               # 'USED_PARTS_QUANTITY': define_data(old_data=self.used_parts_quantity,
                                               #                         new_data=self.parts_qantity_entry_field.get()),
                                               # 'STORAGE_CELL': define_data(old_data=self.storage_cell,
                                               #                               new_data=self.storage_cell_entry_field),
                                               # 'MIN_PERCENT': define_data(old_data=self.min_percent,
                                               #                               new_data=self.min_percent_entry_field)
                                           })
            except sqlite3.ProgrammingError:
                self.input_error_label = Label(self.frame,
                                               text='Ошибка записи данных! Обратитесь к администратору',
                                               foreground='Red')
                self.input_error_label.grid(column=1, row=12)
            else:
                self.quit()
                self.destroy()
                messagebox.showinfo('Уведомление', 'Информация о пресс-форме успешно изменена')
                self.edited_part_data = True

    def confirm_delete(self):
        message = "Вы уверены, что хотите закрыть это окно?"
        if messagebox.askyesno(message=message, parent=self):
            self.destroy()