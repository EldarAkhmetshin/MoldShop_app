#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import tkinter
from os.path import abspath
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from tkinter.ttk import Frame

from src.data import error_messages, columns_customs_report_excel_table, purchased_statuses, DB_NAME
from src.global_values import user_data
from src.utils.excel.xls_tables import export_excel_table, \
    get_purchasing_list_from_excel_file
from src.utils.gui.necessary_spare_parts_report_funcs import get_mold_names_list
from src.utils.logger.logs import get_info_log, get_warning_log
from src.utils.sql_database import new_tables
from src.utils.sql_database.table_funcs import TableInDb


def validate_new_parts_table(column_names: list, rows_data: list) -> bool:
    """
    Функция валидации данных перед их загрузкой в базу данных
    :param rows_data: Список списков с построчной информацией
    :param column_names: Имена столбцов валидируемой таблицы
    :return: Булево значение, характеризующее состояние валидации (пройдена / не пройдена)
    """
    # Проверка на соответствие наименований столбцов
    mold_num_id = None
    element_num_id = None
    element_name_id = None
    purchased_elements_cnt_id = None
    for i, column_name in enumerate(column_names):
        if column_name.lower() == 'номер п/ф':
            mold_num_id = i
        elif column_name.lower() == 'номер запчасти':
            element_num_id = i
        elif column_name.lower() == 'наименование':
            element_name_id = i
        elif column_name.lower() == 'необходимое кол-во, шт':
            purchased_elements_cnt_id = i
    if (mold_num_id is None or element_num_id is None or
            element_name_id is None or purchased_elements_cnt_id is None):
        messagebox.showerror(title='Ошибка',
                             message='Несоответствие названий основных столбцов таблицы')
        return False

    bom_table_names = get_mold_names_list()
    spare_parts = []
    for i, row in enumerate(rows_data):
        mold_num = row[mold_num_id]
        part_num = row[element_num_id]
        part_name = row[element_name_id]
        purchased_parts_cnt = row[purchased_elements_cnt_id]
        # Проверка, что название BOM из таблицы соответствует названию таблицы БД
        if mold_num not in bom_table_names:
            messagebox.showerror(title='Ошибка',
                                 message=f'Строка {i + 2}: Название бома ошибочно')
            return False
        # Проверка, что номер и имя элемента из таблицы имеется в реальном BOM БД
        bom_db = TableInDb(mold_num, DB_NAME)
        if len(bom_db.get_table(type_returned_data='tuple', first_param='NUMBER', first_value=part_num,
                                second_param='PART_NAME', second_value=part_name)) == 0:
            messagebox.showerror(title='Ошибка',
                                 message=f'Строка {i + 2}: Не совпадает элемент спецификации')
            return False
        # Проверка на дублирование по номеру п/ф и запчасти
        if f'{mold_num}_{part_name}' in spare_parts:
            messagebox.showerror(title='Ошибка',
                                 message=f'Строка {i + 2}: Дублирование одинаковых элементов')
            return False
        # Проверка значения в столбце с указанным кол-вом для закупки на правильность типа данных
        if not isinstance(purchased_parts_cnt, int):
            messagebox.showerror(title='Ошибка',
                                 message=f'Строка {i + 2}: Не правильный тип данных. Должно быть число.')
            return False

        spare_parts.append(f'{mold_num}_{part_name}')

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
                if validate_new_parts_table(column_names, rows_data):
                    # Сохранение информации в базе данных
                    new_tables.add_new_purchasing_list(data=rows_data)
                    # Рендер окна приложения с новой загруженной информацией
                    messagebox.showinfo(title='Уведомление',
                                        message='Лист закупаемых запчастей успешно загружен')
                    return True
                else:
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
    purchase_table_db = TableInDb('Purchased_parts', DB_NAME)
    table_purchase_data = purchase_table_db.get_table(type_returned_data='dict', first_param='PURCHASE_NUMBER',
                                                      first_value=purchase_number)

    result_table = []
    for row in table_purchase_data:
        bom_name = row.get('MOLD_NUMBER')
        part_number = row.get('PART_NUMBER')
        part_name = row.get('PART_NAME')
        bom_table_db = TableInDb(bom_name, DB_NAME)
        part_data = bom_table_db.get_table(type_returned_data='dict', first_param='NUMBER',
                                           first_value=part_number,
                                           second_param='PART_NAME', second_value=part_name, last_string=True)
        result_table.append((bom_name, part_number, part_name,
                             row.get('DESCRIPTION'), '0.5', part_data.get('DIMENSIONS'),
                             part_data.get('MATERIAL'), row.get('SUPPLIER'), row.get('QUANTITY')))

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
        super().__init__()
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
        self.focus_set()

        self.init_gui()

    def init_gui(self):
        """
        Инициация контейнеров для размещения виджетов
        """
        self.geometry('315x450')
        self.frame_header = Frame(self)
        self.frame_header.pack(fill=BOTH, expand=True)
        self.frame_body = Frame(self)
        self.frame_body.pack(fill=BOTH, expand=True)
        self.frame_bottom = Frame(self)
        self.frame_bottom.pack(fill=BOTH, expand=True)

    def get_purchase_numbers(self):
        table_db = TableInDb('Purchased_parts', DB_NAME)
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
        get_info_log(user=user_data.get('user_name'), message='Customs report window was rendered',
                     func_name=self.render_widgets.__name__, func_path=abspath(__file__))

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
        # Старт сортировки
        sorted_table = [columns_customs_report_excel_table]
        for purchase_num in selected_purchase_nums:
            sorted_table.extend(sort_table(purchase_num))

        if len(sorted_table) == 1:
            self.input_error_label = Label(self.frame_bottom, text='По вашему запросу ничего не найдено',
                                           foreground='Red')
            self.input_error_label.pack(side=TOP, padx=5, pady=5)
            get_warning_log(user=user_data.get('user_name'), message='NO data for report',
                            func_name=self.create_excel_report.__name__, func_path=abspath(__file__))
        else:
            get_info_log(user=user_data.get('user_name'), message='Data was collected for report',
                         func_name=self.create_excel_report.__name__, func_path=abspath(__file__))
            export_excel_table(sorted_table)


class PurchasedPart(tkinter.Toplevel):
    """
    Класс представляет набор функций для создания графического интерфейса окна и осуществления
    поиска запчастей по заданным параметрам.
    """

    def __init__(self, purchase_number, mold_number, part_number, part_name, purchased_cnt, status, comment):
        """
        Создание переменных
        """
        self.changed_data = None
        self.purchase_number = purchase_number
        self.mold_number = mold_number
        self.part_number = part_number
        self.part_name = part_name
        self.purchased_cnt = purchased_cnt
        self.status = status if status else '-'
        self.comment = comment if comment else '-'

        self.status_combobox = None
        self.comment_entry_field = None

        self.frame_bottom = None
        self.frame_body = None
        self.frame_header = None

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
        ttk.Label(self.frame_body, text='Номер закупки:', style='Regular.TLabel').grid(column=1, row=1,
                                                                                       padx=5, pady=5)
        ttk.Label(self.frame_body, text=self.purchase_number, style='Regular.TLabel').grid(column=2, row=1,
                                                                                           padx=5, pady=5)

        ttk.Label(self.frame_body, text='Номер п/ф:', style='Regular.TLabel').grid(column=1, row=2,
                                                                                   padx=5, pady=5)
        ttk.Label(self.frame_body, text=self.mold_number, style='Regular.TLabel').grid(column=2, row=2,
                                                                                       padx=5, pady=5)

        ttk.Label(self.frame_body, text='Номер запчасти:', style='Regular.TLabel').grid(column=1, row=3,
                                                                                        padx=5, pady=5)
        ttk.Label(self.frame_body, text=self.part_number, style='Regular.TLabel').grid(column=2, row=3,
                                                                                       padx=5, pady=5)

        ttk.Label(self.frame_body, text='Имя запчасти:', style='Regular.TLabel').grid(column=1, row=4,
                                                                                      padx=5, pady=5)
        ttk.Label(self.frame_body, text=self.part_name, style='Regular.TLabel').grid(column=2, row=4,
                                                                                     padx=5, pady=5)

        ttk.Label(self.frame_body, text='Закупленное кол-во:', style='Regular.TLabel').grid(column=1, row=5,
                                                                                            padx=5, pady=5)
        ttk.Label(self.frame_body, text=self.purchased_cnt, style='Regular.TLabel').grid(column=2, row=5,
                                                                                         padx=5, pady=5)

        ttk.Label(self.frame_body, text='Статус:', style='Regular.TLabel').grid(column=1, row=6,
                                                                                padx=5, pady=5)
        ttk.Label(self.frame_body, text=self.status, style='Regular.TLabel').grid(column=2, row=6,
                                                                                  padx=5, pady=5)
        if self.status == purchased_statuses.get('in_process'):
            self.status_combobox = ttk.Combobox(self.frame_body, values=[status_name for status_name
                                                                         in purchased_statuses.values()],
                                                state='readonly')
            self.status_combobox.grid(column=2, row=7, padx=5, pady=5)

        ttk.Label(self.frame_body, text='Комментарий:', style='Regular.TLabel').grid(column=1, row=8,
                                                                                     padx=5, pady=5)
        ttk.Label(self.frame_body, text=self.comment, style='Regular.TLabel').grid(column=2, row=8,
                                                                                   padx=5, pady=5)
        self.comment_entry_field = ttk.Entry(self.frame_body, font=('Times', '11', 'normal'))
        self.comment_entry_field.grid(column=2, row=9, padx=5, pady=5)

        ttk.Button(
            self.frame_bottom, text='Применить', style='Regular.TButton',
            command=self.change_part_status_and_cnt
        ).pack(side=TOP, padx=10, pady=10)
        # Запуск работы окна приложения
        get_info_log(user=user_data.get('user_name'), message='Purchased part window was rendered',
                     func_name=self.render_widgets.__name__, func_path=abspath(__file__))

        self.mainloop()

    def change_part_status_and_cnt(self):
        """
        Функция для изменения информации о статусе закупленной запчасти
        """
        if user_data.get('stock_changing_in') == 'True':
            try:
                new_status = self.status_combobox.get()
            except AttributeError:
                new_status = self.status
            else:
                # Изменение количества запчастей в BOM
                try:
                    bom_db = TableInDb(self.mold_number, DB_NAME)
                    part_info = bom_db.get_table(type_returned_data='dict',
                                                 first_param='NUMBER', first_value=self.part_number,
                                                 second_param='PART_NAME', second_value=self.part_name,
                                                 last_string=True)
                    current_part_cnt = part_info.get('PARTS_QUANTITY')
                    end_quantity = int(self.purchased_cnt) + int(current_part_cnt) if current_part_cnt else int(self.purchased_cnt)
                    bom_db.change_data(first_param='NUMBER', first_value=self.part_number,
                                       data={'PARTS_QUANTITY': end_quantity},
                                       second_param='PART_NAME', second_value=self.part_name)
                except Exception:
                    messagebox.showerror(title='Ошибка',
                                         message=f'Ошибка записи данных. Необходимо обратиться к разработчику')
                    get_warning_log(user=user_data.get('user_name'), message='Error of data changing',
                                    func_name=self.change_part_status_and_cnt.__name__, func_path=abspath(__file__))
            new_comment = self.comment_entry_field.get()
            purchased_parts_db = TableInDb('Purchased_parts', DB_NAME)
            purchased_parts_db.change_data(first_param='PURCHASE_NUMBER', first_value=self.purchase_number,
                                           second_param='PART_NUMBER', second_value=self.part_number,
                                           data={'STATUS': new_status, 'COMMENT': new_comment}
                                           if new_comment else {'STATUS': new_status})

            try:
                self.status_combobox.get()
                messagebox.showinfo('Уведомление', 'Информация о закупаемой запчасти успешно изменена. '
                                                   f'Количество на складе увеличено на {self.purchased_cnt}')
            except AttributeError:
                messagebox.showinfo('Уведомление', 'Информация о закупаемой запчасти успешно сохранена.')

            self.changed_data = True
            self.quit()
            self.destroy()

            get_info_log(user=user_data.get('user_name'), message='Data was successfully changed',
                         func_name=self.change_part_status_and_cnt.__name__, func_path=abspath(__file__))
        else:
            messagebox.showerror(title='Ошибка',
                                 message='Отсутствуют права на приём запчастей')
