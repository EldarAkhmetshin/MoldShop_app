import os
from tkinter import messagebox
from openpyxl import load_workbook

from src.utils.sql_database import table_funcs


def get_data_from_excel_file(file_path: str, work_sheet_name: str):
    """

    :param file_path:
    :param work_sheet_name:
    :return:
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
        for count, row in enumerate(work_sheet.values):
            if not row[0]:
                break

            if count == 0:
                column_names = row
                rows_data.append(row)
            else:
                rows_data.append(row)

        return column_names, rows_data


def save_new_molds_list():
    # Получение данных из Иксель файла
    column_names, rows_data = get_data_from_excel_file(
        file_path=os.path.abspath(os.path.join('..', 'incoming_data', 'molds_data.xlsx')),
        work_sheet_name='Molds')
    # Загрузка данных в базу данных
    molds_data = table_funcs.TableInDb('All_molds_data', 'Database')
    for row in rows_data:
        molds_data.insert_data(row)


def check_mold_number(mold_number: str, hot_runner: bool = None) -> bool:
    """
    Функция проверки наличия номера пресс-формы в общем перечне всех п/ф и проверки на наличие уже созданного ранее BOM с таким номером п/ф
    :param mold_number: Номер пресс-формы
    :param hot_runner: Булево значение, которое характеризует какой тип BOM был выбран (Пресс-форма или горячий канал)
    :return: True - если номер п/ф существует в перечне и такой BOM не создавался ранее 
    """
    define_table_name: Callable = f'BOM_HOT_RUNNER_{mold_number}' if hot_runner else f'BOM_{mold_number}'
    # Выгрузка информации из базы данных
    molds_data = table_funcs.TableInDb('All_molds_data', 'Database')
    molds_table = molds_data.get_table(type_returned_data='tuple')
    # Поиск соответствия через цикл
    for mold_info in molds_table:
        if mold_info[0] == mold_number:
            db = table_funcs.DataBase('Database')
            tables = db.get_all_tables()
            print(tables)
            # Проверка базы данных на наличие схожей таблицы по названию
            new_table = define_table_name()
            for table in tables:
                if table[0] == new_table:
                    return False
            return True
    return False
