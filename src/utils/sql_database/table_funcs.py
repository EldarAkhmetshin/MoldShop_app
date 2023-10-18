#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import sqlite3
import os
from os.path import abspath
from abc import abstractmethod, ABC
from loguru import logger
from typing import Any, List, Dict, Callable


from src.utils.logger.logs import get_info_log, get_warning_log


class DataBase():

    def __init__(self, name: str):
        """
        Функция инициирует новый экземпляр из базы данных
        :param name:  Имя базы данных
        :param cursor: Область в памяти базы данных, предназначенная для хранения последнего оператора SQL.
        :param connection: Переменная для получения доступа к базе данных и внесению изменений в ней
        """
        self._name = name
        self._cursor = None
        self._connection = None

    @property
    def name(self):
        """
        Функция инкапсуляции переменной
        """
        return self._name

    @property
    def cursor(self):
        """
        Функция инкапсуляции переменной
        """
        return self._cursor

    @property
    def connection(self):
        """
        Функция инкапсуляции переменной
        """
        return self._connection

    @cursor.setter
    def cursor(self, cursor):
        """
        Функция «безопасного» изменения переменной
        """
        self._cursor = cursor

    @connection.setter
    def connection(self, connection):
        """
        Функция «безопасного» изменения переменной
        """
        self._connection = connection

    def connect_db(self):
        """
        Функция подключения к базе данных для взаимодействия с ней
        """
        path = os.path.abspath(os.path.join('savings', 'database', f'{self.name}.db'))
        #path = os.path.abspath(os.path.join(f'{self.name}.db'))
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()

    def get_all_tables(self) -> list:
        """
        Функция возвращает список с наименованием всех таблиц в базе данных
        :return tables: Список наименований всех таблиц базы данных
        """
        self.connect_db()
        self.cursor.execute(''' SELECT name FROM sqlite_master WHERE type = "table"''' )
        tables = self.cursor.fetchall()
        self.cursor.close()
        return tables


class TableInDb(DataBase):

    def __init__(self, table_name: str, database_name: str):
        """
        Функция инициирует новый экземпляр из таблицы базы данных
        :param table_name:  Имя таблицы
        :param database_name: Имя базы данных
        """
        super().__init__(database_name)
        self.table_name = table_name

    def crt_new_table_and_connect_db(self, table_params: dict):
        """
        Функция создает новую таблицу и добавляет столбцы в неё
        :param table_params: Словарь с перечисленными новыми столбцами таблицы {Имя столбца: Формат данных для этого столбца}
        """
        self.connect_db()
        cnt = 0
        for i_param, i_type in table_params.items():
            if cnt == 0:
                cnt += 1
                self.cursor.execute(f''' CREATE TABLE IF NOT EXISTS {self.table_name}({i_param} {i_type})''')
                print(f'New table {self.table_name} and new column {i_param} with type {i_type} successfully added')
            else:
                self.add_column({i_param: i_type})
        self.connection.commit()
        self.cursor.close()

    def add_column(self, table_params: dict):
        """
        Функция добавления новых столбцов в таблицу
        :param table_params: Словарь с перечисленными новыми столбцами таблицы {Имя столбца: Формат данных для этого столбца}
        """
        self.connect_db()
        for i_param, i_type in table_params.items():
            try:
                self.cursor.execute(f''' ALTER TABLE {self.table_name} ADD COLUMN {i_param} {i_type}''')
            except sqlite3.OperationalError:
                get_warning_log(user='-', message=f'Duplicate column {i_param}', func_name= self.add_column.__name__,
                                func_path=abspath(__file__))
            else:
                print(f'New column {i_param} with type {i_type} successfully added')
        self.connection.commit()
        self.cursor.close()

    def check_data_in_table(self, param: str, value: (str, int)):
        result = self.cursor.execute(f'SELECT * FROM {self.table_name} WHERE {param}={value}')
        return result.fetchone() is None

    def insert_data(self, info: tuple):
        """
        Функция создает новую строку в таблице и вставляет данные в каждый столбец
        :param info: Кортеж со значениями новой строки в таблице
        """
        self.connect_db()
        cols = tuple(i_param[1] for i_param in self.cursor.execute(f'PRAGMA table_info ({self.table_name});'))
        values = list(map(lambda num: '?, ' if num != len(cols) - 1 else '?', range(len(cols))))
        values = ''.join(values)

        try:
            self.cursor.execute(f'INSERT INTO {self.table_name}{cols} VALUES({values});', info)
        except sqlite3.DatabaseError as error:
            logger.exception(f'{error}')
        else:
            get_info_log(user='', message=f'New data were added', func_name=self.insert_data.__name__,
                         func_path=abspath(__file__))
        self.connection.commit()
        self.cursor.close()

    def change_data(self, param: str, value: (str, int), data: dict):
        """
        Функция изменения значений в таблице в соответствии с запрошенными параметрами

        :param param: Имя столбца / параметра на который будет ориентирован поиск
        :param value: Значение параметра для поиска
        :param data: Словарь с  новыми данными для изменения значений в найденной строке таблицы ({Название столбца / параметра: Новое значение})
        """
        self.connect_db()
        for i_key, i_value in data.items():
            self.cursor.execute(f'UPDATE {self.table_name} Set {i_key} = ?'
                                f'WHERE {param} = ?', (i_value, value))
        self.connection.commit()
        self.cursor.close()

    def get_table(self, type_returned_data: str, first_param: str = None, first_value: str | int = None,
                  last_string: bool = None, second_param: str = None, second_value: str | int = None,
                  third_param: str = None, rhird_value: str = None) \
            -> List[dict] | List[tuple] | Dict:
        """
        Функция получения данных из таблицы базы данных в соответствии с запрошенными параметрами

        :param type_returned_data: Формат возращаемой информации в массиве данных (словарь или кортеж).
        :param first_param: Имя 1-го столбца / параметра на который будет ориентирован поиск
        :param first_value: Значение 1-го параметра для поиска
        :param last_string: Булево значение для получения только 1-й последней строки удовлетворяющей запрашиваемым параметрам 
        :param second_param: Имя 2-го столбца / параметра на который будет ориентирован поиск
        :param second_value: Значение 2-го параметра для поиска
        :param second_param: Имя 3-го столбца / параметра на который будет ориентирован поиск
        :param second_value: Значение 3-го параметра для поиска

        :return: all_info: Возвращаемая информация согласно запрашиваемым параметрам
        """
        self.connect_db()
        if not first_value:
            self.cursor.execute(f'SELECT * FROM {self.table_name}')
        elif first_param and first_value:
            self.cursor.execute(f'SELECT * FROM {self.table_name} WHERE {first_param} = "{first_value}" ')
        elif first_param and first_value and second_param and second_value:
            self.cursor.execute(f'SELECT * FROM {self.table_name} WHERE {first_param} = "{first_value}" '
                                f'AND {second_param} = "{second_value}"')
        elif first_param and first_value and second_param and second_value and third_param and third_value:
            self.cursor.execute(f'SELECT * FROM {self.table_name} WHERE {first_param} = "{first_value}" '
                                f'AND {second_param} = "{second_value}" '
                                f'AND {third_param} = "{third_value}"')

        result = self.cursor.fetchall()
        columns = tuple(i_param[1] for i_param in self.cursor.execute(f'PRAGMA table_info ({self.table_name});'))
        self.cursor.close()
        all_info = []

        if type_returned_data == 'dict':
            for i_res in result:
                info = {}
                for i_num, i_value in enumerate(i_res):
                    info[columns[i_num]] = i_value
                all_info.append(info)
            all_info_check: Callable = lambda: all_info if not last_string else all_info[len(all_info) - 1]
            return all_info_check()

        elif type_returned_data == 'tuple':
            return result

    def delete_data(self, column_name: str, value: (str, int)):
        """
        Функция удаляет данные из таблицы в соответствии с запрошенными параметрами и значениями
        :param column_name: Имя столбца / параметра для поиска в таблице
        :param value: Значение из указанного столбца удаляемой строки
        """
        self.connect_db()
        self.cursor.execute(f"DELETE FROM {self.table_name} WHERE {column_name}='{value}';")
        self.connection.commit()
        self.cursor.close()

    def delete_db_table(self):
        """
        Функция удаляет таблицу из базы данных
        """
        self.connect_db()
        self.cursor.execute(f"DROP TABLE {self.table_name}")
        self.connection.commit()
        self.cursor.close()

        
