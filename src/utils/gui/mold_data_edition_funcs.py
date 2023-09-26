#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import sqlite3
import tkinter
from tkinter import *
from tkinter import messagebox, ttk
from tkinter.ttk import Frame, Combobox
from typing import Callable

from ttkthemes.themed_style import ThemedStyle

from src.config_data.config import passwords
from src.global_values import user_data
from src.utils.sql_database import table_funcs
from src.data import mold_statuses_list


class EditedMold(tkinter.Toplevel):
    """
    Класс представляет набор функций для создания графического интерфейса окна редактирования
    информации о пресс-формы из общего переченя.
    """

    def __init__(self, mold_data: dict = None):
        """
        Создание переменных
        """
        if mold_data:
            self.mold_data = mold_data
        else:
            self.mold_data = {}
        self.location_entry_field = None
        self.status_entry_field = None
        self.hot_runner_maker_entry_field = None
        self.mold_maker_entry_field = None
        self.cavities_qnt_entry_field = None
        self.release_date_entry_field = None
        self.product_name_entry_field = None
        self.mold_name_entry_field = None
        self.hot_runner_entry_field = None
        self.mold_num_entry_field = None
        self.mold_number = self.mold_data.get('MOLD_NUMBER')
        self.hot_runner_number = self.mold_data.get('HOT_RUNNER_NUMBER')
        self.mold_name = self.mold_data.get('MOLD_NAME')
        self.product_name = self.mold_data.get('PRODUCT_NAME')
        self.release_year = self.mold_data.get('RELEASE_YEAR')
        self.cavities_quantity = self.mold_data.get('CAVITIES_QUANTITY')
        self.mold_maker = self.mold_data.get('MOLD_MAKER')
        self.hot_runner_maker = self.mold_data.get('HOT_RUNNER_MAKER')
        self.status = self.mold_data.get('STATUS')
        self.location = self.mold_data.get('LOCATION')

        self.changed_data = None
        self.input_error_label = None
        self.frame = None
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.confirm_delete)
        self.init_gui()

    def init_gui(self):
        """Инициация окна приложения и контейнера для размещения виджетов"""
        self.focus_set()
        self.grab_set()
        self.frame = Frame(self)
        self.frame.pack()

    def get_label_and_entry_widgets_in_row(self, text: str, point_info: str, row: int,
                                           necessary_field: bool = None, mold_status_widget: bool = None) \
            -> tkinter.ttk.Combobox | tkinter.Entry:
        """
        Рендер виджетов окна расположенных в одной строке
        :param text: Текст надписи
        :param point_info: Текущее значение (до изменения)
        :param row: Номер строки в окне
        :param necessary_field: Булево значение о необходимости заполнения данных
        :param mold_status_widget: Булево значение передающее True, если рендериться строка о статусе п/ф
        :return: Виджет поля ввода
        """
        ttk.Label(self.frame, text=text, style='Regular.TLabel').grid(column=1, row=row, padx=5, pady=5)
        if self.mold_data:
            entry_column_num = 3
            ttk.Label(self.frame, text=point_info, style='Regular.TLabel').grid(column=2, row=row, padx=5, pady=5)
        else:
            entry_column_num = 2

        if necessary_field and not self.mold_data:
            ttk.Label(self.frame, text='*', style='Regular.TLabel').grid(column=4, row=row)
        if mold_status_widget:
            combobox = ttk.Combobox(self.frame, values=mold_statuses_list, state='readonly')
            combobox.grid(pady=5, column=entry_column_num, row=row)
            return combobox
        else:
            entry_field = ttk.Entry(self.frame, style='Regular.TEntry')
            entry_field.grid(pady=5, padx=2, column=entry_column_num, row=row)
            return entry_field

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна ввода информации о новой пресс-форме
        """
        define_title: Callable = lambda: 'Редактирование информации о пресс-форме' \
            if self.mold_data else 'Новая пресс-форма'

        ttk.Label(self.frame, text=define_title(), style='Title.TLabel').grid(column=2, row=1, pady=15)

        self.mold_num_entry_field = self.get_label_and_entry_widgets_in_row(text='№ формы', point_info=self.mold_number,
                                                                            row=2, necessary_field=True)
        self.hot_runner_entry_field = self.get_label_and_entry_widgets_in_row(text='№ горячего канала',
                                                                              point_info=self.hot_runner_number, row=3)
        self.mold_name_entry_field = self.get_label_and_entry_widgets_in_row(text='Наименование',
                                                                             point_info=self.mold_name,
                                                                             row=4, necessary_field=True)
        self.product_name_entry_field = self.get_label_and_entry_widgets_in_row(text='Название продукции',
                                                                                point_info=self.product_name,
                                                                                row=5, necessary_field=True)
        self.release_date_entry_field = self.get_label_and_entry_widgets_in_row(text='Год выпуска',
                                                                                point_info=self.release_year,
                                                                                row=6, necessary_field=True)
        self.cavities_qnt_entry_field = self.get_label_and_entry_widgets_in_row(text='Количество гнёзд',
                                                                                point_info=self.cavities_quantity,
                                                                                row=7, necessary_field=True)
        self.mold_maker_entry_field = self.get_label_and_entry_widgets_in_row(text='Производитель',
                                                                              point_info=self.mold_maker,
                                                                              row=8, necessary_field=True)
        self.hot_runner_maker_entry_field = self.get_label_and_entry_widgets_in_row(text='Производитель г. к.',
                                                                                    point_info=self.hot_runner_maker,
                                                                                    row=9)
        self.status_entry_field = self.get_label_and_entry_widgets_in_row(text='Статус', row=10, point_info=self.status,
                                                                          necessary_field=True, mold_status_widget=True)
        self.location_entry_field = self.get_label_and_entry_widgets_in_row(text='Местонахождение',
                                                                            point_info=self.location, row=11)

        if self.mold_data:
            ttk.Button(
                self.frame, text='Применить', style='Regular.TButton',
                command=self.validate_and_save_edited_mold_data
            ).grid(padx=10, pady=10, column=2, row=13)
        else:
            ttk.Button(
                self.frame, text='Применить', style='Regular.TButton',
                command=self.validate_and_save_new_mold_data
            ).grid(padx=10, pady=10, column=2, row=13)
        # Запуск работы окна приложения
        self.mainloop()

    def validate_and_save_new_mold_data(self):
        """
        Фнкция проверки введённых данных пользователем
        """
        # Проверка правильности ввода информации о годе выпуска пресс формы и количестве гнёзд
        if self.input_error_label:
            self.input_error_label.destroy()
        try:
            release_date = int(self.release_date_entry_field.get())
            cavities_qnt = int(self.cavities_qnt_entry_field.get())
        except ValueError:
            self.input_error_label = Label(self.frame,
                                           text='В графах "Год выпуска" и "Количество гнёзд" '
                                                'должны быть числовые значения',
                                           foreground='Red')
            self.input_error_label.grid(column=1, row=12)
        else:
            # Проверка на заполнение обязательных полей
            mold_num = self.mold_num_entry_field.get()
            mold_name = self.mold_name_entry_field.get()
            mold_maker = self.mold_maker_entry_field.get()
            status = self.status_entry_field.get()
            if mold_num and mold_name and mold_maker and status:
                # Загрузка данных в базу данных
                row = (
                    mold_num, self.hot_runner_entry_field.get(), mold_name, self.product_name_entry_field.get(),
                    release_date, cavities_qnt, mold_maker, self.hot_runner_maker_entry_field.get(),
                    status, self.location_entry_field.get()
                )
                try:
                    molds_data = table_funcs.TableInDb('All_molds_data', 'Database')
                    molds_data.insert_data(info=row)
                except sqlite3.ProgrammingError:
                    self.input_error_label = Label(self.frame,
                                                   text='Ошибка записи данных! Обратитесь к администратору',
                                                   foreground='Red')
                    self.input_error_label.grid(column=1, row=12)
                else:
                    self.quit()
                    self.destroy()
                    messagebox.showinfo('Уведомление',
                                        'Информация о новой пресс-форме успешно добавлена в общий перечень')
                    self.changed_data = True
            # Если данные введены некорректно пользователь получит уведомление об ошибке
            else:
                self.input_error_label = Label(self.frame,
                                               text='Не корректный ввод данных', foreground='Red')
                self.input_error_label.grid(column=1, row=12)

    def validate_and_save_edited_mold_data(self):
        """
        Фнкция проверки введённых данных пользователем
        """
        # Проверка правильности ввода информации о годе выпуска пресс формы и количестве гнёзд
        if self.input_error_label:
            self.input_error_label.destroy()
        try:
            release_date = self.release_date_entry_field.get()
            cavities_qnt = self.cavities_qnt_entry_field.get()
            if release_date:
                int(release_date)
            if cavities_qnt:
                int(cavities_qnt)
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
                molds_data = table_funcs.TableInDb('All_molds_data', 'Database')
                molds_data.change_data(param='MOLD_NUMBER', value=self.mold_number,
                                       data={
                                           'MOLD_NUMBER': define_data(old_data=self.mold_number,
                                                                      new_data=self.mold_num_entry_field.get()),
                                           'HOT_RUNNER_NUMBER': define_data(old_data=self.hot_runner_number,
                                                                            new_data=self.hot_runner_entry_field.get()),
                                           'MOLD_NAME': define_data(old_data=self.mold_name,
                                                                    new_data=self.mold_name_entry_field.get()),
                                           'PRODUCT_NAME': define_data(old_data=self.product_name,
                                                                       new_data=self.product_name_entry_field.get()),
                                           'RELEASE_YEAR': define_data(old_data=self.release_year,
                                                                       new_data=self.release_date_entry_field.get()),
                                           'CAVITIES_QUANTITY': define_data(old_data=self.cavities_quantity,
                                                                            new_data=self.cavities_qnt_entry_field.get()),
                                           'MOLD_MAKER': define_data(old_data=self.mold_maker,
                                                                     new_data=self.mold_maker_entry_field.get()),
                                           'HOT_RUNNER_MAKER': define_data(old_data=self.hot_runner_maker,
                                                                           new_data=self.hot_runner_maker_entry_field.get()),
                                           'STATUS': define_data(old_data=self.status,
                                                                 new_data=self.status_entry_field.get()),
                                           'LOCATION': define_data(old_data=self.location,
                                                                   new_data=self.location_entry_field.get())})
            except sqlite3.ProgrammingError:
                self.input_error_label = ttk.Label(self.frame,
                                                   text='Ошибка записи данных! Обратитесь к администратору',
                                                   foreground='Red')
                self.input_error_label.grid(column=1, row=12)
            else:
                self.quit()
                self.destroy()
                messagebox.showinfo('Уведомление', 'Информация о пресс-форме успешно изменена')
                self.changed_data = True

    def confirm_delete(self):
        message = "Вы уверены, что хотите закрыть это окно?"
        if messagebox.askyesno(message=message, parent=self):
            self.destroy()