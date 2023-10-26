#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Frame
from typing import Callable

from src.data import columns_searching_results, columns_sizes_warehouse_table
from src.utils.sql_database.table_funcs import DataBase, TableInDb


class Searcher(tkinter.Toplevel):
    """
    Класс представляет набор функций для создания графического интерфейса окна изменения количества какого либо элемента на складе.
    """

    def __init__(self):
        """
        Создание переменных
        """
        self.results_window = None
        self.checkbutton = None
        self.product_type_combobox = None
        self.additional_info_entry_field = None
        self.description_entry_field = None
        self.name_entry_field = None
        self.tree = None
        self.frame_bottom = None
        self.frame_body = None
        self.frame_header = None
        self.text_entry_field = None
        self.search_filter_combobox = None
        self.stock = StringVar()
        self.results = []
        self.input_error_label = None
        super().__init__()
        self.focus_set()
        self.init_gui()

    def init_gui(self):
        """
        Инициация окна приложения и контейнеров для размещения виджетов
        """
        self.frame_header = Frame(self)
        self.frame_header.pack(fill=BOTH, expand=True)
        self.frame_body = Frame(self)
        self.frame_body.pack(fill=BOTH, expand=True)
        self.frame_bottom = Frame(self)
        self.frame_bottom.pack(fill=BOTH, expand=True)

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна ввода информации
        """
        ttk.Label(self.frame_header, text='Поиск запчастей', style='Title.TLabel').pack(side=TOP, pady=15)

        ttk.Label(self.frame_body, text='Параметры поиска:', style='Regular.TLabel').grid(column=1, row=1, padx=5, pady=10)

        ttk.Label(self.frame_body, text='Наименование', style='Regular.TLabel').grid(column=1, row=2, padx=5, pady=5)
        self.name_entry_field = ttk.Entry(self.frame_body, font=('Times', '11', 'normal'))
        self.name_entry_field.grid(column=2, row=2, padx=5, pady=5)

        ttk.Label(self.frame_body, text='Описание', style='Regular.TLabel').grid(column=1, row=3, padx=5, pady=5)
        self.description_entry_field = ttk.Entry(self.frame_body, font=('Times', '11', 'normal'))
        self.description_entry_field.grid(column=2, row=3, padx=5, pady=5)

        ttk.Label(self.frame_body, text='Доп. информация', style='Regular.TLabel').grid(column=1, row=4, padx=5, pady=5)
        self.additional_info_entry_field = ttk.Entry(self.frame_body, font=('Times', '11', 'normal'))
        self.additional_info_entry_field.grid(column=2, row=4, padx=5, pady=5)

        ttk.Label(self.frame_body, text='Составляющая', style='Regular.TLabel').grid(column=1, row=5, padx=5, pady=5)
        self.product_type_combobox = ttk.Combobox(self.frame_body, values=['Пресс-форма', 'Горячий канал', 'Все'],
                                                  state='readonly')
        self.product_type_combobox.grid(column=2, row=5, padx=5, pady=5)

        ttk.Label(self.frame_body, text='Наличие на складе', style='Regular.TLabel').grid(column=1, row=6, padx=5, pady=5)
        self.checkbutton = ttk.Checkbutton(self.frame_body, variable=self.stock, offvalue='False', onvalue='True')
        self.checkbutton.grid(column=2, row=6, padx=5, pady=5)

        ttk.Button(
            self.frame_bottom, text='Применить', style='Regular.TButton',
            command=self.start_search
        ).pack(side=TOP, padx=10, pady=10)
        # Запуск работы окна приложения
        self.mainloop()

    def render_results(self):
        """
        Функция рендера результатов поиска в табличном виде в дополнительном окне
        """
        if len(self.results) == 0:
            self.input_error_label = Label(self.frame_bottom, text='По вашему запросу ничего не найдено', foreground='Red')
            self.input_error_label.pack(side=TOP, padx=5, pady=5)
        else:
            if self.results_window and self.tree:
                self.tree.pack_forget()
                self.results_window.destroy()
            # рендер дополнительного окна для вывода результатов
            self.results_window = tkinter.Toplevel()
            self.results_window.title('Searching Results')
            self.results_window.geometry('640x480')
            self.results_window.focus_set()
            # определяем таблицу
            self.tree = ttk.Treeview(self.results_window, columns=columns_searching_results, show="headings")
            self.tree.pack(fill=BOTH, expand=1)
            # определяем заголовки
            for col_name in columns_searching_results:
                self.tree.heading(col_name, text=col_name)
            # настраиваем столбцы
            for col_num, col_size in columns_sizes_warehouse_table.items():
                self.tree.column(column=col_num, stretch=YES, width=col_size)
            for row in self.results:
                self.tree.insert("", END, values=row)
            self.results = []
            get_info_log(user=user_data.get('user_name'), message='Results of searching were rendered',
                                     func_name=self.render_results.__name__, func_path=abspath(__file__))

    def sort_table(self, table_name):
        """
        Функция сортировки данных в таблице базы данных по введённым ранее параметрам, а также запись полученных данных в массив с результатами поискоаого запроса
        :param table_name: Имя таблицы, в которой осуществляется поиск
        """
        define_mold_type: Callable = lambda: 'Горячий канал' if 'HOT_RUNNER' in table_name else 'Пресс-форма'
        bom = TableInDb(table_name, 'Database')
        table_list = bom.get_table(type_returned_data='dict', first_param='PART_NAME',
                                   first_value=self.name_entry_field.get(),
                                   second_param='DESCRIPTION',
                                   second_value=self.description_entry_field.get(),
                                   third_param='ADDITIONAL_INFO',
                                   third_value=self.additional_info_entry_field.get())
        for row in table_list:
            try:
                if ((self.stock.get() == 'True' and int(row.get('PARTS_QUANTITY')) > 0) or self.stock.get() == 'False'
                        or self.stock.get() == ''):
                    self.results.append((define_mold_type(), table_name.replace('BOM_', '').replace('HOT_RUNNER_', ''),
                                         row.get('PART_NAME'), row.get('DESCRIPTION'),
                                         row.get('ADDITIONAL_INFO'), row.get('PARTS_QUANTITY'),
                                         row.get('USED_PARTS_QUANTITY')))
            except TypeError:
                pass

    def start_search(self):
        """
        Функция проведения поиска запчастей по введённым ранее параметрам
        """
        get_info_log(user=user_data.get('user_name'), message='Searching is run',
                                     func_name=self.start_search.__name__, func_path=abspath(__file__))
        if self.input_error_label:
            self.input_error_label.destroy()
        # Получение всех наименований доступных таблиц для поиска по ним
        db = DataBase('Database')
        tables_names = db.get_all_tables()
        # Старт сортировки если один из параметров заполнен
        if self.name_entry_field or self.description_entry_field or self.additional_info_entry_field:
            for table in tables_names:
                if (self.product_type_combobox.get() == 'Пресс-форма' and 'HOT_RUNNER' not in table[0]
                        and 'BOM' in table[0]):
                    self.sort_table(table[0])
                elif self.product_type_combobox.get() == 'Горячий канал' and 'HOT_RUNNER' in table[0] and 'BOM':
                    self.sort_table(table[0])
                elif ((self.product_type_combobox.get() == 'Все' or self.product_type_combobox.get() == '')
                      and 'BOM' in table[0]):
                    self.sort_table(table[0])
            self.render_results()

        else:
            self.input_error_label = Label(self.frame_bottom, text='По вашему запросу ничего не найдено', foreground='Red')
            self.input_error_label.pack(side=TOP, padx=5, pady=5)
