#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import sqlite3
import tkinter
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Frame, Combobox

from src.config_data.config import passwords
from src.global_values import user_data
from src.utils.sql_database import table_funcs
from src.data import mold_statuses_list


class NewMold(tkinter.Toplevel):
    """
    Класс представляет набор функций для создания графического интерфейса окна добавления новой пресс-формы в общий перечень.
    """

    def __init__(self):
        """
        Создание переменных
        """
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
        self.new_mold_information = None
        self.input_error_label = None
        self.frame = None
        super().__init__()
        self.init_gui()

    def init_gui(self):
        """
        Инициация окна приложения и контейнера для размещения виджетов
        """
        self.focus_set()
        self.grab_set()
        self.frame = Frame(self)
        self.frame.pack()

    def get_label_and_entry_widgets_in_row(self, text: str, row: int,
                                           necessary_field: bool = None, mold_status_widget: bool = None) \
            -> tkinter.ttk.Combobox | tkinter.Entry:
        """
        Рендер виджетов окна расположенных в одной строке
        :param text: Текст надписи
        :param row: Номер строки в окне
        :param necessary_field: Булево значение о необходимости заполнения данных
        :param mold_status_widget: Булево значение передающее True, если рендериться строка о статусе п/ф
        :return: Виджет поля ввода
        """
        Label(self.frame, text=text).grid(column=1, row=row, padx=5, pady=5)

        if necessary_field:
            Label(self.frame, text='*', font=('Times', '13')).grid(column=3, row=row)
        if mold_status_widget:
            combobox = Combobox(self.frame, values=mold_statuses_list, state='readonly')
            combobox.grid(pady=5, column=2, row=row)
            return combobox
        else:
            entry_field = Entry(self.frame, font=('Times', '10', 'bold'))
            entry_field.grid(pady=5, column=2, row=row)
            return entry_field

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна ввода информации о новой пресс-форме
        """
        Label(self.frame, text='Новая пресс-форма', font=('Times', '15', 'bold')).grid(column=2, row=1, pady=15)

        self.mold_num_entry_field = self.get_label_and_entry_widgets_in_row(text='№ формы', row=2, necessary_field=True)
        self.hot_runner_entry_field = self.get_label_and_entry_widgets_in_row(text='№ горячего канала', row=3)
        self.mold_name_entry_field = self.get_label_and_entry_widgets_in_row(text='Наименование', row=4,
                                                                             necessary_field=True)
        self.product_name_entry_field = self.get_label_and_entry_widgets_in_row(text='Название продукции', row=5,
                                                                                necessary_field=True)
        self.release_date_entry_field = self.get_label_and_entry_widgets_in_row(text='Год выпуска', row=6,
                                                                                necessary_field=True)
        self.cavities_qnt_entry_field = self.get_label_and_entry_widgets_in_row(text='Количество гнёзд', row=7,
                                                                                necessary_field=True)
        self.mold_maker_entry_field = self.get_label_and_entry_widgets_in_row(text='Производитель', row=8,
                                                                              necessary_field=True)
        self.hot_runner_maker_entry_field = self.get_label_and_entry_widgets_in_row(text='Производитель г. к.', row=9)
        self.status_entry_field = self.get_label_and_entry_widgets_in_row(text='Статус', row=10,
                                                                          necessary_field=True, mold_status_widget=True)
        self.location_entry_field = self.get_label_and_entry_widgets_in_row(text='Местонахождение', row=11)

        Button(
            self.frame, text='Применить', background='white',
            width=20, font=('Times', '10'),
            command=lambda: self.validate_and_save_new_mold_data()
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
                    self.new_mold_information = True
            # Если данные введены некорректно пользователь получит уведомление об ошибке
            else:
                self.input_error_label = Label(self.frame,
                                               text='Не корректный ввод данных', foreground='Red')
                self.input_error_label.grid(column=1, row=12)
