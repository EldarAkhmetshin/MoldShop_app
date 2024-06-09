from typing import Callable
from datetime import datetime

from src.data import purchased_statuses, DB_NAME
from src.utils.sql_database import table_funcs
from src.utils.sql_database.table_funcs import DataBase, TableInDb


def create_bom_for_new_mold(mold_number: str, rows_data: list, hot_runner: bool = None):
    """
    Создание новой таблицы в базе данных.
    :param hot_runner: Булево значение True если таблица сохраняется для BOM горячего канала
    :param mold_number: Номер пресс-формы
    :param rows_data: Список строк для сохранения в базу данных
    """
    # Загрузка информации в базу данных
    define_table_name: Callable = lambda: f'BOM_HOT_RUNNER_{mold_number}' if hot_runner else f'BOM_{mold_number}'
    bom = table_funcs.TableInDb(define_table_name(), DB_NAME)
    bom.crt_new_table_and_connect_db(table_params={'NUMBER': 'TEXT', 'PART_NAME': 'TEXT',
                                                   'PCS_IN_MOLDS': 'TEXT', 'DESCRIPTION': 'TEXT',
                                                   'ADDITIONAL_INFO': 'TEXT', 'SUPPLIER': 'TEXT',
                                                   'MATERIAL': 'TEXT', 'DIMENSIONS': 'TEXT', 'PARTS_QUANTITY': 'TEXT',
                                                   'USED_PARTS_QUANTITY': 'TEXT', 'STORAGE_CELL': 'TEXT',
                                                   'MIN_PERCENT': 'TEXT', 'WEIGHT': 'REAL'})

    for row in rows_data:
        bom.insert_data(row)


def add_new_purchasing_list(data: list):
    """
    Функция для добавления списка новой партии закупленных запчастей в таблицу базы данных
    """
    purchased_parts = table_funcs.TableInDb('Purchased_parts', DB_NAME)
    try:
        last_purchased_part = purchased_parts.get_table(type_returned_data='dict', last_string=True)
    except IndexError:
        purchase_num = 0
    else:
        purchase_num = int(last_purchased_part.get('PURCHASE_NUMBER'))
    for row in data:
        row = list(row)
        row.insert(0, purchase_num + 1)
        row.insert(1, datetime.now().strftime("%m/%d/%Y, %H:%M"))
        # Удаление не нужных значений
        row.pop(len(row) - 2)
        row.pop(len(row) - 2)
        # Добавление значений статуса закупки и комментария
        row.append(purchased_statuses.get('in_process'))
        row.append(None)

        purchased_parts.insert_data(tuple(row))


def create_tables_in_db():
    """
    Функция создаёт новую базу данных и таблицы если они ещё не существуют.
    Таблица "All_molds_data" содержит сводную информацию обо всех пресс-формах на балансе компании.
    """

    molds_data = table_funcs.TableInDb('All_molds_data', DB_NAME)
    molds_data.crt_new_table_and_connect_db(
        table_params={'MOLD_NUMBER': 'TEXT', 'HOT_RUNNER_NUMBER': 'TEXT',
                      'MOLD_NAME': 'TEXT', 'PRODUCT_NAME': 'TEXT',
                      'RELEASE_YEAR': 'TEXT', 'CAVITIES_QUANTITY': 'TEXT',
                      'MOLD_MAKER': 'TEXT', 'HOT_RUNNER_MAKER': 'TEXT',
                      'STATUS': 'TEXT', 'LOCATION': 'TEXT'})

    moving_history = table_funcs.TableInDb('Molds_moving_history', DB_NAME)
    moving_history.crt_new_table_and_connect_db(
        table_params={'DATE': 'TEXT', 'USER': 'TEXT', 'MOLD_NUMBER': 'TEXT', 'MOLD_NAME': 'TEXT',
                      'LAST_STATUS': 'TEXT', 'NEXT_STATUS': 'TEXT'})

    in_warehouse_history = table_funcs.TableInDb('IN_warehouse_history', DB_NAME)
    in_warehouse_history.crt_new_table_and_connect_db(
        table_params={'DATE': 'TEXT', 'USER': 'TEXT', 'MOLD_NUMBER': 'TEXT', 'PART_NUMBER': 'TEXT', 'PART_NAME': 'TEXT',
                      'PART_TYPE': 'TEXT', 'QUANTITY': 'INT'})

    out_warehouse_history = table_funcs.TableInDb('OUT_warehouse_history', DB_NAME)
    out_warehouse_history.crt_new_table_and_connect_db(
        table_params={'DATE': 'TEXT', 'USER': 'TEXT', 'MOLD_NUMBER': 'TEXT', 'PART_NUMBER': 'TEXT', 'PART_NAME': 'TEXT',
                      'PART_TYPE': 'TEXT', 'QUANTITY': 'INT'})

    purchased_parts = table_funcs.TableInDb('Purchased_parts', DB_NAME)
    purchased_parts.crt_new_table_and_connect_db(
        table_params={'PURCHASE_NUMBER': 'TEXT', 'DATE': 'TEXT', 'MOLD_NUMBER': 'TEXT', 'PART_TYPE': 'TEXT',
                      'PART_NUMBER': 'TEXT', 'PART_NAME': 'TEXT', 'DESCRIPTION': 'TEXT', 'QUANTITY': 'INT',
                      'STATUS': 'TEXT', 'COMMENT': 'TEXT'})


def add_columns_bom_table(columns: dict):
    """
    Функция для добавления новых столбцов в уже существующие БОМы
    """
    database = DataBase(DB_NAME)
    table_names = database.get_all_tables()
    bom_table_names = list(filter(lambda table_name: 'BOM' in table_name, table_names))
    for table in bom_table_names:
        bom_db = TableInDb(table, DB_NAME)
        bom_db.add_column(table_params=columns)


def delete_titles_row_bom_table():
    """
    Функция для удаления заголовков из существующих БОМов
    """
    database = DataBase(DB_NAME)
    table_names = database.get_all_tables()
    bom_table_names = list(filter(lambda table_name: 'BOM' in table_name, table_names))
    for table in bom_table_names:
        bom_db = TableInDb(table, DB_NAME)
        bom_db.delete_data(column_name='NUMBER', value='№ по парт листу')
