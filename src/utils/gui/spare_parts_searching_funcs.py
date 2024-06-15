#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import tkinter
from dataclasses import dataclass
from os.path import abspath
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Frame, Combobox
from typing import Callable, List

from src.data import columns_searching_results, columns_sizes_warehouse_table
from src.global_values import user_data
from src.utils.gui.necessary_spare_parts_report_funcs import get_mold_names_list
from src.utils.logger.logs import get_info_log, get_warning_log
from src.utils.sql_database.table_funcs import TableInDb


@dataclass
class Searcher(tkinter.Toplevel):
    """
    Класс представляет набор функций для создания графического интерфейса окна и осуществления
    поиска запчастей по заданным параметрам.
    """
    results_window: Toplevel = None
    checkbutton: Checkbutton = None
    product_type_combobox: Combobox = None
    additional_info_entry_field: Entry = None
    description_entry_field: Entry = None
    name_entry_field: Entry = None
    tree: ttk.Treeview = None
    text_entry_field: Entry = None
    search_filter_combobox: Combobox = None
    input_error_label: Label = None

    def __post_init__(self):
        """
        Инициация контейнеров для размещения виджетов и некоторых переменных
        """
        super().__init__()
        self.focus_set()
        self.frame_header: Frame = Frame(self)
        self.frame_body: Frame = Frame(self)
        self.frame_bottom: Frame = Frame(self)

        self.frame_header.pack(fill=BOTH, expand=True)
        self.frame_body.pack(fill=BOTH, expand=True)
        self.frame_bottom.pack(fill=BOTH, expand=True)

        self.spare_part_status: StringVar = StringVar()
        self.results: List = []

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна ввода информации
        """
        ttk.Label(self.frame_header, text='Поиск запчастей', style='Title.TLabel').pack(side=TOP, pady=15)

        ttk.Label(self.frame_body, text='Параметры поиска:', style='Regular.TLabel').grid(column=1, row=1, padx=5,
                                                                                          pady=10)

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
        self.product_type_combobox = Combobox(self.frame_body, values=['Пресс-форма', 'Горячий канал', 'Все'],
                                              state='readonly')
        self.product_type_combobox.grid(column=2, row=5, padx=5, pady=5)

        ttk.Label(self.frame_body, text='Наличие на складе', style='Regular.TLabel').grid(column=1, row=6, padx=5,
                                                                                          pady=5)
        self.checkbutton = ttk.Checkbutton(self.frame_body, variable=self.spare_part_status,
                                           offvalue='False', onvalue='True')
        self.checkbutton.grid(column=2, row=6, padx=5, pady=5)

        ttk.Button(
            self.frame_bottom, text='Применить', style='Regular.TButton',
            command=self.start_search
        ).pack(side=TOP, padx=10, pady=10)
        # Запуск работы окна приложения
        get_info_log(user=user_data.get('user_name'), message='Searching window was rendered',
                     func_name=self.render_widgets.__name__,
                     func_path=abspath(__file__))
        self.mainloop()

    def render_results(self):
        """
        Функция рендера результатов поиска в табличном виде в дополнительном окне
        """
        if len(self.results) == 0:
            self.input_error_label = Label(self.frame_bottom, text='По вашему запросу ничего не найдено',
                                           foreground='Red')
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
            # Отчистка списка с результами поиска
            self.results.clear()
            get_info_log(user=user_data.get('user_name'), message='Results of searching were rendered',
                         func_name=self.render_results.__name__, func_path=abspath(__file__))

    def sort_table(self, table_name):
        """
        Функция сортировки данных в таблице базы данных по введённым ранее параметрам, а также запись полученных данных
        в массив с результатами поискового запроса
        :param table_name: Имя таблицы, в которой осуществляется поиск
        """
        define_mold_type: Callable = lambda: 'Горячий канал' if 'HOT_RUNNER' in table_name else 'Пресс-форма'
        bom = TableInDb(table_name, 'Database')
        capitalize_results = bom.get_table(type_returned_data='dict', first_param='PART_NAME',
                                           first_value=self.name_entry_field.get().capitalize(),
                                           second_param='DESCRIPTION',
                                           second_value=self.description_entry_field.get().capitalize(),
                                           third_param='ADDITIONAL_INFO',
                                           third_value=self.additional_info_entry_field.get().capitalize())
        lower_results = bom.get_table(type_returned_data='dict', first_param='PART_NAME',
                                      first_value=self.name_entry_field.get().lower(),
                                      second_param='DESCRIPTION',
                                      second_value=self.description_entry_field.get().lower(),
                                      third_param='ADDITIONAL_INFO',
                                      third_value=self.additional_info_entry_field.get().lower())
        upper_results = bom.get_table(type_returned_data='dict', first_param='PART_NAME',
                                      first_value=self.name_entry_field.get().upper(),
                                      second_param='DESCRIPTION',
                                      second_value=self.description_entry_field.get().upper(),
                                      third_param='ADDITIONAL_INFO',
                                      third_value=self.additional_info_entry_field.get().upper())
        table_list = []
        table_list.extend(capitalize_results)
        table_list.extend(lower_results)
        table_list.extend(upper_results)
        sorted_table = map(dict, set(tuple(sorted(result.items())) for result in table_list))
        for row in sorted_table:
            if row.get('DESCRIPTION') == 'Описание':
                pass
            else:
                try:
                    if ((self.spare_part_status.get() == 'True' and
                         int(row.get('PARTS_QUANTITY')) > 0) or self.spare_part_status.get() == 'False' or
                            self.spare_part_status.get() == ''):
                        self.results.append(
                            (define_mold_type(), table_name.replace('BOM_', '').replace('HOT_RUNNER_', ''),
                             row.get('PART_NAME'), row.get('DESCRIPTION'),
                             row.get('ADDITIONAL_INFO'), row.get('PARTS_QUANTITY'),
                             row.get('USED_PARTS_QUANTITY')))
                except (TypeError, ValueError):
                    pass

    def start_search(self):
        """
        Функция проведения поиска запчастей по введённым ранее параметрам
        """
        get_info_log(user=user_data.get('user_name'), message='Searching was run',
                     func_name=self.start_search.__name__, func_path=abspath(__file__))
        if self.input_error_label:
            self.input_error_label.destroy()
        # Получение всех наименований доступных таблиц для поиска по ним
        tables_names = get_mold_names_list()
        # Старт сортировки если один из параметров заполнен
        if self.name_entry_field.get() or self.description_entry_field.get() or self.additional_info_entry_field.get():
            for table in tables_names:
                if (self.product_type_combobox.get() == 'Пресс-форма' and 'HOT_RUNNER' not in table
                        and 'BOM' in table):
                    self.sort_table(table)
                elif self.product_type_combobox.get() == 'Горячий канал' and 'HOT_RUNNER' in table and 'BOM':
                    self.sort_table(table)
                elif ((self.product_type_combobox.get() == 'Все' or self.product_type_combobox.get() == '')
                      and 'BOM' in table):
                    self.sort_table(table)
            self.render_results()
            get_info_log(user=user_data.get('user_name'), message='Searching was completed with results',
                         func_name=self.start_search.__name__, func_path=abspath(__file__))

        else:
            self.input_error_label = Label(self.frame_bottom, text='По вашему запросу ничего не найдено',
                                           foreground='Red')
            self.input_error_label.pack(side=TOP, padx=5, pady=5)
            get_warning_log(user=user_data.get('user_name'), message='Searching was completed without results',
                            func_name=self.start_search.__name__, func_path=abspath(__file__))
