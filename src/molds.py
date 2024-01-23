import os
from tkinter import messagebox
from openpyxl import load_workbook
from typing import Callable

from src.data import columns_bom_parts_table
from src.utils.sql_database import table_funcs


def get_data_from_excel_file(file_path: str, work_sheet_name: str) -> (tuple, list):
    """
    Функция для получения информации из Excel файла
    :param file_path: Путь к Excel файлу
    :param work_sheet_name: Наименование листа Excel файла откуда будет браться информация
    :return: Кортеж из наименований столбцов таблицы
    :return: Массив данных из полученной таблицы. Каждая строка таблицы записана в отдельный кортеж
    """
    column_names = None
    rows_data = []

    work_book = load_workbook(file_path)
    try:
        work_sheet = work_book[f'{work_sheet_name}']
    except KeyError:
        messagebox.showerror('Уведомление об ошибке',
                             'Название листа не соотвествует. Убедитесь, что вы используете правильный файл шаблона')
    else:
        part_nums = []
        for count, row in enumerate(work_sheet.values):
            # Проверка на наличие номера запчасти в каждой строке и на то, чтобы этот номер не повторялся в BOM
            part_num = row[0]
            if not part_num:
                return (column_names, rows_data,
                        False, 'BOM не может быть загружен, так как имеется строка без номера запчасти')
            elif part_num in part_nums:
                return (column_names, rows_data,
                        False, f'BOM не может быть загружен, так как номер запчасти {row[0]} дублируется')

            if count == 0:
                column_names = row
                rows_data.append(row)
            else:
                rows_data.append(row)
            part_nums.append(part_num)

        return column_names, rows_data, True, None


def save_new_molds_list():
    # Получение данных из Иксель файла
    column_names, rows_data = get_data_from_excel_file(
        file_path=os.path.abspath(os.path.join('..', 'incoming_data', 'molds_data.xlsx')),
        work_sheet_name='Molds')
    # Загрузка данных в базу данных
    molds_data = table_funcs.TableInDb('All_molds_data', 'Database')
    for row in rows_data:
        molds_data.insert_data(row)


def validate_new_bom(mold_number: str, column_names: tuple, hot_runner: bool = None) -> bool:
    """
    Функция проверки наличия номера пресс-формы в общем перечне всех п/ф, проверки на наличие уже созданного ранее BOM с таким номером п/ф,
    а также проверки на соотвествие названий столбцов таблицы из нового BOM
    :param mold_number: Номер пресс-формы
    :param column_names: Наименования столбцов нового BOM
    :param hot_runner: Булево значение, которое характеризует какой тип BOM был выбран (Пресс-форма или горячий канал)
    :return: True - если номер п/ф существует в перечне и такой BOM не создавался ранее 
    """
    define_table_name: Callable = lambda: f'BOM_HOT_RUNNER_{mold_number}' if hot_runner else f'BOM_{mold_number}'
    # Выгрузка информации из базы данных
    molds_data = table_funcs.TableInDb('All_molds_data', 'Database')
    molds_table = molds_data.get_table(type_returned_data='tuple')
    # Поиск соответствия через цикл
    for mold_info in molds_table:
        if mold_info[0] == mold_number:
            db = table_funcs.DataBase('Database')
            tables = db.get_all_tables()
            # Проверка базы данных на наличие схожей таблицы по названию
            new_table = define_table_name()
            for table in tables:
                if table[0] == new_table:
                    return False
            # Проверка названий столбцов нового бома на корректность
            for num, name in enumerate(columns_bom_parts_table):
                if name != column_names[num]:
                    return False
            return True
    return False
