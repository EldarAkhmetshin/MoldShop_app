#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import tkinter
from dataclasses import dataclass
from os.path import abspath
from tkinter import *
from tkinter import ttk
from tkinter.ttk import Frame
from typing import Callable, List
from math import ceil

from src.data import columns_searching_results, columns_sizes_warehouse_table, columns_min_parts_excel_table, DB_NAME
from src.global_values import user_data
from src.utils.excel.xls_tables import export_excel_table
from src.utils.logger.logs import get_info_log, get_warning_log
from src.utils.sql_database.table_funcs import DataBase, TableInDb


def sort_table(table_name):
    """
    Функция сортировки данных в таблице базы данных по введённым ранее параметрам, а также запись полученных данных
    в массив с результатами поискового запроса
    :param table_name: Имя таблицы, в которой осуществляется поиск
    """
    define_mold_type: Callable = lambda: 'Горячий канал' if 'HOT_RUNNER' in table_name else 'Пресс-форма'
    check_min_availability: Callable = lambda: True if parts_quantity / parts_quantity_in_mold * 100 < \
        min_part_percent else False
    bom = TableInDb(table_name, DB_NAME)
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
                necessary_parts_quantity = ceil((parts_quantity_in_mold / 100 * min_part_percent) - parts_quantity)
                result_table.append((table_name, define_mold_type(), row.get('NUMBER'), row.get('PART_NAME'),
                                     row.get('DESCRIPTION'), row.get('PCS_IN_MOLDS'), row.get('PARTS_QUANTITY'),
                                     necessary_parts_quantity))

    return result_table


def get_mold_names_list() -> list:
    """
    Функция для получения наименований всех БОМов имеющихся в текущей базе данных
    """
    database = DataBase(DB_NAME)
    table_names = database.get_all_tables()
    return list(filter(lambda table_name: 'BOM' in table_name, table_names))


@dataclass
class MinPartsReport(tkinter.Toplevel):
    """
    Класс представляет набор функций для создания графического интерфейса окна и осуществления
    поиска запчастей по заданным параметрам.
    """
    molds_list_box: Listbox = None
    results_window: Tk = None
    checkbutton: Checkbutton = None
    product_type_combobox: ttk.Combobox = None
    additional_info_entry_field: Entry = None
    description_entry_field: Entry = None
    name_entry_field: Entry = None
    tree: ttk.Treeview = None
    text_entry_field: Entry = None
    search_filter_combobox: ttk.Combobox = None
    input_error_label: Label = None

    def __post_init__(self):
        """
        Инициация контейнеров для размещения виджетов и некоторых переменных
        """
        super().__init__()
        self.focus_set()
        self.geometry('330x500')
        self.frame_header: Frame = Frame(self)
        self.frame_body: Frame = Frame(self)
        self.frame_bottom: Frame = Frame(self)

        self.frame_header.pack(fill=BOTH, expand=True)
        self.frame_body.pack(fill=BOTH, expand=True)
        self.frame_bottom.pack(fill=BOTH, expand=True)

        self.spare_part_status: StringVar = StringVar()
        self.results: List = []

    # def __init__(self):
    #     """
    #     Создание переменных
    #     """
    #     self.molds_list_box = None
    #     self.results_window = None
    #     self.checkbutton = None
    #     self.product_type_combobox = None
    #     self.additional_info_entry_field = None
    #     self.description_entry_field = None
    #     self.name_entry_field = None
    #     self.tree = None
    #     self.frame_bottom = None
    #     self.frame_body = None
    #     self.frame_header = None
    #     self.text_entry_field = None
    #     self.search_filter_combobox = None
    #     self.spare_part_status = StringVar()
    #     self.results = []
    #     self.input_error_label = None
    #     super().__init__()
    #     self.focus_set()
    #     self.init_gui()
    #
    # def init_gui(self):
    #     """
    #     Инициация контейнеров для размещения виджетов
    #     """
    #     self.geometry('330x450')
    #     self.frame_header = Frame(self)
    #     self.frame_header.pack(fill=BOTH, expand=True)
    #     self.frame_body = Frame(self)
    #     self.frame_body.pack(fill=BOTH, expand=True)
    #     self.frame_bottom = Frame(self)
    #     self.frame_bottom.pack(fill=BOTH, expand=True)

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна ввода информации
        """
        ttk.Label(self.frame_header, text='Дефектация', style='Title.TLabel').pack(side=TOP, pady=15)

        (ttk.Label(self.frame_body, text='Выделите из списка ниже необходимые п/ф', style='Regular.TLabel')
         .pack(side=TOP, pady=10))
        self.molds_list_box = Listbox(self.frame_body, selectmode=MULTIPLE, width=140)
        bom_table_names = get_mold_names_list()
        self.molds_list_box.insert(0, *bom_table_names)
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
        get_info_log(user=user_data.get('user_name'), message='Min parts searching window was rendered',
                     func_name=self.render_widgets.__name__, func_path=abspath(__file__))
        self.mainloop()

    def start_search(self):
        """
        Функция проведения поиска запчастей по введённым ранее параметрам
        """
        sorted_table = [columns_min_parts_excel_table]

        if self.input_error_label:
            self.input_error_label.destroy()
        # Получение всех наименований, которые были выделены пользователем
        selection = self.molds_list_box.curselection()
        selected_table_names = [self.molds_list_box.get(i) for i in selection]
        # Старт сортировки
        for table in selected_table_names:
            sorted_table.extend(sort_table(table))
        if len(sorted_table) == 1:
            get_warning_log(user=user_data.get('user_name'), message='Searching was completed without results',
                            func_name=self.start_search.__name__, func_path=abspath(__file__))
            self.input_error_label = Label(self.frame_bottom, text='По вашему запросу ничего не найдено',
                                           foreground='Red')
            self.input_error_label.pack(side=TOP, padx=5, pady=5)
        else:
            get_info_log(user=user_data.get('user_name'), message='Searching was completed with results',
                         func_name=self.start_search.__name__, func_path=abspath(__file__))
            export_excel_table(sorted_table)
