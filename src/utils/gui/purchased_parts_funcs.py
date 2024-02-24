#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import tkinter
from os.path import abspath
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from tkinter.ttk import Frame
from typing import Callable

from src.data import columns_searching_results, columns_sizes_warehouse_table, columns_min_parts_excel_table, \
    error_messages, columns_customs_report_excel_table
from src.global_values import user_data
from src.utils.excel.xls_tables import export_excel_table, \
    get_purchasing_list_from_excel_file
from src.utils.logger.logs import get_info_log, get_warning_log
from src.utils.sql_database import new_tables
from src.utils.sql_database.table_funcs import TableInDb


def validate_new_parts_table(column_names: list) -> bool:
    """
    Функция валидации данных перед их загрузкой в базу данных
    :param column_names: Имена столбцов валидируемой таблицы
    :return: Булево значение, характеризующее состояние валидации (пройдена / не пройдена)
    """
    column_names = 5
    return True


def upload_purchased_parts() -> bool:
    """
    Функция загрузки списка закупаемых запчастей из Иксель файла формата xlsx в таблицу базы данных
    """
    # Открытие диалогового окна для выбора файла пользователем с локальной директории компьютера,
    # с дальнейшим извлечением пути к выбранному файлу в виде строки
    if user_data.get('purchased_parts_uploading') == 'True':
        try:
            file_path = filedialog.askopenfile(
                filetypes=(('XLSX files', '*.xlsx'),)
            ).name
        except AttributeError:
            pass
        else:
            # Получение информации из Иксель файла типа xlsx
            try:
                column_names, rows_data, status, error_massage = get_purchasing_list_from_excel_file(
                    file_path=file_path,
                    work_sheet_name='Table')
                if not status:
                    messagebox.showerror(title='Ошибка загрузки',
                                         message=error_massage)
                    return False
            except TypeError:
                get_warning_log(user=user_data.get('user_name'), message='New purchasing list wasnt uploaded',
                                func_name=upload_purchased_parts.__name__, func_path=abspath(__file__))
            else:
                # Поиск соответствия по номеру пресс-формы в общем перечне
                if validate_new_parts_table(column_names=column_names):
                    # Сохранение информации в базе данных
                    new_tables.add_new_purchasing_list(data=rows_data)
                    # Рендер окна приложения с новой загруженной информацией
                    messagebox.showinfo(title='Уведомление',
                                        message='Лист закупаемых запчастей успешно загружен')
                    return True
                else:
                    messagebox.showerror(title='Ошибка',
                                         message='Информация не может быть загружена по причине некорректного '
                                                 'заполнения таблицы')
                    return False
    else:
        messagebox.showerror(error_messages.get('access_denied').get('message_name'),
                             error_messages.get('access_denied').get('message_body'))
        return False


def sort_table(purchase_number: str) -> list:
    """
    Функция сортировки данных в таблице базы данных по введённым ранее параметрам, а также запись полученных данных
    в массив с результатами поискового запроса
    :param purchase_number: Номер закупки, по которой нужно составить отчёт
    :return: Таблица с результатами сортировки данных в виде листа с кортежами внутри
    """
    purchase_table_db = TableInDb('Purchased_parts', 'Database')
    table_purchase_data = purchase_table_db.get_table(type_returned_data='dict', first_param='PURCHASE_NUMBER',
                                                      first_value=purchase_number)

    result_table = []
    for row in table_purchase_data:
        bom_name = row.get('MOLD_NUMBER')
        part_number = row.get('PART_NUMBER')
        part_name = row.get('PART_NAME')
        bom_table_db = TableInDb(bom_name, 'Database')
        part_data = bom_table_db.get_table(type_returned_data='dict', first_param='NUMBER',
                                           first_value=part_number,
                                           second_param='PART_NAME', second_value=part_name, last_string=True)
        result_table.append((bom_name, part_number, part_name,
                             row.get('DESCRIPTION'), '0.5', part_data.get('DIMENSIONS'),
                             part_data.get('MATERIAL'), row.get('QUANTITY')))

    return result_table


class CustomsReport(tkinter.Toplevel):
    """
    Класс представляет набор функций для создания графического интерфейса окна и осуществления
    поиска запчастей по заданным параметрам.
    """

    def __init__(self):
        """
        Создание переменных
        """
        self.purchase_numbers_list_box = None
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

    def get_purchase_numbers(self):
        table_db = TableInDb('Purchased_parts', 'Database')
        last_table_string = table_db.get_table(type_returned_data='dict', last_string=True)
        last_purchase_number = int(last_table_string.get('PURCHASE_NUMBER'))
        purchase_numbers = tuple(number for number in range(1, last_purchase_number + 1))
        self.purchase_numbers_list_box.insert(0, *purchase_numbers)

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна ввода информации
        """
        ttk.Label(self.frame_header, text='Выгрузка для таможни', style='Title.TLabel').pack(side=TOP, pady=15)

        (ttk.Label(self.frame_body, text='Выделите из списка необходимые\nномера закупок для выгрузки',
                   style='Regular.TLabel')
         .pack(side=TOP, pady=10))
        self.purchase_numbers_list_box = Listbox(self.frame_body, selectmode=MULTIPLE, width=140)
        self.get_purchase_numbers()
        scroll = Scrollbar(self.frame_body, orient=tkinter.VERTICAL, command=self.purchase_numbers_list_box.yview)
        scroll.pack(side=RIGHT, fill=Y)
        self.purchase_numbers_list_box.configure(yscrollcommand=scroll.set)
        self.purchase_numbers_list_box.pack(side=TOP, pady=10)
        ttk.Button(
            self.frame_bottom, text='Применить', style='Regular.TButton',
            command=self.create_excel_report
        ).pack(side=TOP, padx=10, pady=10)
        # Запуск работы окна приложения
        self.mainloop()

    def create_excel_report(self):
        """
        Функция проведения поиска запчастей по введённым ранее параметрам
        """
        get_info_log(user=user_data.get('user_name'), message='Searching is run',
                     func_name=self.create_excel_report.__name__, func_path=abspath(__file__))
        if self.input_error_label:
            self.input_error_label.destroy()
        # Получение всех наименований, которые были выделены пользователем
        selection = self.purchase_numbers_list_box.curselection()
        selected_purchase_nums = [self.purchase_numbers_list_box.get(i) for i in selection]
        print(selected_purchase_nums)
        # Старт сортировки
        sorted_table = [columns_customs_report_excel_table]
        for purchase_num in selected_purchase_nums:
            sorted_table.extend(sort_table(purchase_num))
        if len(sorted_table) == 1:
            self.input_error_label = Label(self.frame_bottom, text='По вашему запросу ничего не найдено',
                                           foreground='Red')
            self.input_error_label.pack(side=TOP, padx=5, pady=5)
        else:
            export_excel_table(sorted_table)
