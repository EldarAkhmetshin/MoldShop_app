from src.utils.sql_database import table_funcs


def create_bom_for_new_mold(mold_number: str, rows_data: list, hot_runner: bool = None):
    """
    Создание новой таблицы в базе данных.
    :param hot_runner: Булево значение True если таблица сохраняется для BOM горячекого канала
    :param mold_number: Номер пресс-формы
    :param rows_data: Список строк для сохранения в базу данных
    """
    # Загрузка информации в базу данных
    if hot_runner:
        bom = table_funcs.TableInDb(table_name=f'BOM_HOT_RUNNER_{mold_number}', database_name='Database')
    else:
        bom = table_funcs.TableInDb(table_name=f'BOM_{mold_number}', database_name='Database')
    bom.crt_new_table_and_connect_db(table_params={'NUMBER': 'TEXT', 'PART_NAME': 'TEXT',
                                                   'PCS_IN_MOLDS': 'TEXT', 'DESCRIPTION': 'TEXT',
                                                   'ADDITIONAL_INFO': 'TEXT', 'SUPPLIER': 'TEXT',
                                                   'MATERIAL': 'TEXT', 'DIMENSIONS': 'TEXT', 'PARTS_QUANTITY': 'TEXT',
                                                   'USED_PARTS_QUANTITY': 'TEXT', 'STORAGE_CELL': 'TEXT',
                                                   'MIN_PERCENT': 'TEXT'})

    for row in rows_data:
        bom.insert_data(row)


def create_tables_in_db():
    """
    Функция создаёт новую базу данных и таблицы если они ещё не существуют.
    Таблица "All_molds_data" содержит сводную информацию обо всех пресс-формах на балансе компании.
    """

    molds_data = table_funcs.TableInDb('All_molds_data', 'Database')
    molds_data.crt_new_table_and_connect_db(
        table_params={'MOLD_NUMBER': 'TEXT', 'HOT_RUNNER_NUMBER': 'TEXT',
                      'MOLD_NAME': 'TEXT', 'PRODUCT_NAME': 'TEXT',
                      'RELEASE_YEAR': 'TEXT', 'CAVITIES_QUANTITY': 'TEXT',
                      'MOLD_MAKER': 'TEXT', 'HOT_RUNNER_MAKER': 'TEXT',
                      'STATUS': 'TEXT', 'LOCATION': 'TEXT'})

    moving_history = table_funcs.TableInDb('Molds_moving_history', 'Database')
    moving_history.crt_new_table_and_connect_db(
        table_params={'DATE': 'TEXT', 'USER': 'TEXT', 'MOLD_NUMBER': 'TEXT', 'MOLD_NAME': 'TEXT',
                      'LAST_STATUS': 'TEXT', 'NEXT_STATUS': 'TEXT'})

    in_warehouse_history = table_funcs.TableInDb('IN_warehouse_history', 'Database')
    in_warehouse_history.crt_new_table_and_connect_db(
        table_params={'DATE': 'TEXT', 'USER': 'TEXT', 'MOLD_NUMBER': 'TEXT', 'PART_NUMBER': 'TEXT', 'PART_NAME': 'TEXT',
                      'PART_TYPE': 'TEXT', 'QUANTITY': 'INT'})

    out_warehouse_history = table_funcs.TableInDb('OUT_warehouse_history', 'Database')
    out_warehouse_history.crt_new_table_and_connect_db(
        table_params={'DATE': 'TEXT', 'USER': 'TEXT', 'MOLD_NUMBER': 'TEXT', 'PART_NUMBER': 'TEXT', 'PART_NAME': 'TEXT',
                      'PART_TYPE': 'TEXT', 'QUANTITY': 'INT'})
