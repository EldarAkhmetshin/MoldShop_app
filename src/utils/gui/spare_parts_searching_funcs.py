#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import sqlite3
import tkinter
from datetime import datetime
from tkinter import *
from tkinter import messagebox, ttk
from tkinter.ttk import Frame
from typing import Callable

from src.config_data.config import passwords
from src.global_values import user_data
from src.utils.sql_database import table_funcs


class Searcher(tkinter.Toplevel):
    """
    Класс представляет набор функций для создания графического интерфейса окна изменения количества какого либо элемента на складе.
    """

    def __init__(self):
        """
        Создание переменных
        """
        self.frame_bottom = None
        self.frame_body = None
        self.frame_header = None
        self.text_entry_field = None
        self.search_filter_combobox = None
        self.mold = IntVar()
        self.hot_runner = IntVar()
        self.stock = IntVar()
        self.input_error_label = None
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.confirm_delete)
        self.init_gui()

    def init_gui(self):
        """
        Инициация окна приложения и контейнеров для размещения виджетов
        """
        self.frame_header = Frame(self)
        self.frame_header.pack()
        self.frame_body = Frame(self)
        self.frame_body.pack()
        self.frame_bottom = Frame(self)
        self.frame_bottom.pack()

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна ввода информации
        """
        ttk.Label(self.frame_header, text='Поиск запчастей', style='Title.TLabel').pack(side=TOP, pady=15)
      
        ttk.Label(self.frame_body, text='Параметры', style='Regular.TLabel').grid(column=1, row=1, padx=5, pady=10)
      
        ttk.Label(self.frame_body, text='Наименование', style='Regular.TLabel').grid(column=2, row=2, padx=5, pady=5)
        self.name_entry_field = ttk.Entry(self.frame_body, font=('Times', '11', 'normal'))
        self.name_entry_field.grid(column=2, row=2, padx=5, pady=5)

        ttk.Label(self.frame_body, text='Описание', style='Regular.TLabel').grid(column=2, row=3, padx=5, pady=5)
        self.description_entry_field = ttk.Entry(self.frame_body, font=('Times', '11', 'normal'))
        self.description_entry_field.grid(column=2, row=3, padx=5, pady=5)

        ttk.Label(self.frame_body, text='Изготовитель', style='Regular.TLabel').grid(column=2, row=4, padx=5, pady=5)
        self.maker_entry_field = ttk.Entry(self.frame_body, font=('Times', '11', 'normal'))
        self.maker_entry_field.grid(column=2, row=4, padx=5, pady=5)      

        ttk.Label(self.frame_body, text='Пресс-форма', style='Regular.TLabel').grid(column=2, row=5, padx=5, pady=5)
        ttk.Checkbutton(variable=self.mold).grid(column=2, row=5, padx=5, pady=5)

        ttk.Label(self.frame_body, text='Горячий канал', style='Regular.TLabel').grid(column=2, row=6, padx=5, pady=5)
        ttk.Checkbutton(variable=self.hot_runner).grid(column=2, row=6, padx=5, pady=5)
        
        ttk.Label(self.frame_body, text='Наличие на складе', style='Regular.TLabel').grid(column=2, row=7, padx=5, pady=5)
        ttk.Checkbutton(variable=self.stock).grid(column=2, row=7, padx=5, pady=5)
        
        ttk.Button(
            self.frame_bottom, text='Применить', style='Regular.TButton',
            command=self.validate_and_save_changed_data
        ).pack(padx=10, pady=10, side=TOP)
        # Запуск работы окна приложения
        self.mainloop()

    def start_search(self):
        """
        Функция проведения поиска запчастей по введённым ранее параметрам
        """
        if self.input_error_label:
            self.input_error_label.destroy()
        # Получение всех наименований доступных таблиц для поиска по ним
        db = DataBase('Database')
        tables_names = db.get_all_tables()
        # Старт сортировки если один из параметров заполнен
        if self.name_entry_field or self.description_entry_field or self.maker_entry_field:
            for table in tables_names:
              bom = TableInDb(table, 'Database')
          
        else:
            self.input_error_label = Label(self.frame_bottom,
                                           text='По вашему запросу ничего не найдено', foreground='Red')
            self.input_error_label.grid(side=TOP, padx=5, pady=5)

    def confirm_delete(self):
        message = "Вы уверены, что хотите закрыть это окно?"
        if messagebox.askyesno(message=message, parent=self):
            self.destroy()
