from src.utils.sql_database import table_funcs


def create_bom_for_new_mold(mold_number: str, rows_data: list):
    """
    Создание новой таблицы в базе данных.
    :param mold_number: Номер пресс-формы
    :param rows_data: Список строк для сохранения в базу данных
    """
    # Загрузка информации в базу данных
    mold_bom = table_funcs.TableInDb(table_title=f'BOM_{mold_number}', database_name='Database')
    mold_bom.crt_new_table_and_connect_db(table_params={'NUMBER': 'TEXT', 'PART_NAME': 'TEXT',
                                                        'PCS_IN_MOLDS': 'TEXT', 'DESCRIPTION': 'TEXT',
                                                        'ADDITIONAL_INFO': 'TEXT', 'SUPPLIER': 'TEXT',
                                                        'MATERIAL': 'TEXT', 'DIMENSIONS': 'TEXT'})

    for row in rows_data[2:]:
        mold_bom.insert_data(row)


def create_tables_in_db():
    """
    Функция создаёт новую базу данных и таблицы если они ещё не существуют.
    Таблица "All_molds_data" содержит сводную информацию обо всех пресс-формах на балансе компании.
    """

    molds_data = table_funcs.TableInDb('All_molds_data', 'Database')
    molds_data.crt_new_table_and_connect_db(table_params={'MOLD_NUMBER': 'TEXT', 'HOT_RUNNER_NUMBER': 'TEXT',
                                                          'MOLD_NAME': 'TEXT', 'PRODUCT_NAME': 'TEXT',
                                                          'RELEASE_YEAR': 'TEXT', 'CAVITIES_QUANTITY': 'TEXT',
                                                          'MOLD_MAKER': 'TEXT', 'HOT_RUNNER_MAKER': 'TEXT',
                                                          'STATUS': 'TEXT', 'LOCATION': 'TEXT'})
