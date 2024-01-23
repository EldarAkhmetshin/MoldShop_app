#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import tkinter
from os.path import abspath
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Frame
from typing import Callable

from src.data import columns_searching_results, columns_sizes_warehouse_table, columns_min_parts_excel_table
from src.global_values import user_data
from src.utils.logger.logs import get_info_log
from src.utils.sql_database.table_funcs import DataBase, TableInDb


def sort_table(table_name):
    """
    Функция сортировки данных в таблице базы данных по введённым ранее параметрам, а также запись полученных данных
    в массив с результатами поискового запроса
    :param table_name: Имя таблицы, в которой осуществляется поиск
    """
    define_mold_type: Callable = lambda: 'Горячий канал' if 'HOT_RUNNER' in table_name else 'Пресс-форма'
    check_min_availability: Callable = lambda: True if parts_quantity / parts_quantity_in_mold * 100 < min_part_percent else False
    bom = TableInDb(table_name, 'Database')
    table_data = bom.get_table(type_returned_data='dict')
    result_table = []
    for row in table_data:
        try:
            parts_quantity = int(row.get('PARTS_QUANTITY'))
        except (ValueError, TypeError):
            parts_quantity = 0
        try:
            parts_quantity_in_mold = int(row.get('PCS_IN_MOLDS'))
            min_part_percent = int(row.get('MIN_PERCENT'))
        except (ValueError, TypeError):
            pass
        else:
            if check_min_availability():
                result_table.append((table_name, define_mold_type(), row.get('NUMBER'), row.get('PART_NAME'),
                                     row.get('DESCRIPTION'), row.get('PCS_IN_MOLDS'), row.get('PARTS_QUANTITY')))

    return result_table


class MinPartsReport(tkinter.Toplevel):
    """
    Класс представляет набор функций для создания графического интерфейса окна и осуществления
    поиска запчастей по заданным параметрам.
    """

    def __init__(self):
        """
        Создание переменных
        """
        self.molds_list_box = None
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
        self.geometry('315x450')
        self.frame_header = Frame(self)
        self.frame_header.pack(fill=BOTH, expand=True)
        self.frame_body = Frame(self)
        self.frame_body.pack(fill=BOTH, expand=True)
        self.frame_bottom = Frame(self)
        self.frame_bottom.pack(fill=BOTH, expand=True)

    def get_mold_titles(self):
        database = DataBase('Database')
        table_names = database.get_all_tables()
        bom_table_names = list(filter(lambda table_name: 'BOM' in table_name[0], table_names))
        self.molds_list_box.insert(0, *bom_table_names)

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна ввода информации
        """
        ttk.Label(self.frame_header, text='Дефектация', style='Title.TLabel').pack(side=TOP, pady=15)

        (ttk.Label(self.frame_body, text='Выделите из списка ниже необходимые п/ф', style='Regular.TLabel')
         .pack(side=TOP, pady=10))
        self.molds_list_box = Listbox(self.frame_body, selectmode=MULTIPLE, width=140)
        self.get_mold_titles()
        scroll = Scrollbar(self.frame_body, orient=tkinter.VERTICAL, command=self.molds_list_box.yview)
        scroll.pack(side=RIGHT, fill=Y)
        self.molds_list_box.configure(yscrollcommand=scroll.set)
        self.molds_list_box.pack(side=TOP, pady=10)
        (ttk.Label(self.frame_body, text='ПРИМЕЧАНИЕ: Запчасть будет учитываться в '
                                         '\nвыгрузке если будут заполнены ячейки в столбцах:'
                                         '\n - Количество в форме;'
                                         '\n - В наличие (новые), шт;'
                                         '\n - Допустимый остаток,%', style='Regular.TLabel')
         .pack(side=TOP, pady=4))
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
            self.results = []
            get_info_log(user=user_data.get('user_name'), message='Results of searching were rendered',
                         func_name=self.render_results.__name__, func_path=abspath(__file__))

    def start_search(self):
        """
        Функция проведения поиска запчастей по введённым ранее параметрам
        """
        from src.main_app_funcs import save_excel_table

        sorted_table = [columns_min_parts_excel_table]
        get_info_log(user=user_data.get('user_name'), message='Searching is run',
                     func_name=self.start_search.__name__, func_path=abspath(__file__))
        if self.input_error_label:
            self.input_error_label.destroy()
        # Получение всех наименований, которые были выделены пользователем
        selection = self.molds_list_box.curselection()
        selected_table_names = [self.molds_list_box.get(i)[0] for i in selection]
        # Старт сортировки
        for table in selected_table_names:
            sorted_table.extend(sort_table(table))
        if len(sorted_table) == 1:
            self.input_error_label = Label(self.frame_bottom, text='По вашему запросу ничего не найдено',
                                           foreground='Red')
            self.input_error_label.pack(side=TOP, padx=5, pady=5)
        else:
            save_excel_table(sorted_table)
