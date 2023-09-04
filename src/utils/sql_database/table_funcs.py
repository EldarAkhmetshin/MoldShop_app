#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import sqlite3
import os
from os.path import abspath
from abc import abstractmethod, ABC
from loguru import logger
from typing import Any, List, Dict, Callable


from src.utils.logger.logs import get_info_log, get_warning_log


class DataBase(ABC):

    @abstractmethod
    def __init__(self, name: str) -> None:
        """
        Function initiate the new object from the database
        :param name:  title
        """
        self._name = name
        self._cursor = None
        self._connection = None

    @property
    def name(self):
        """
        Encapsulation function
        :return:name: Database title
        """
        return self._name

    @property
    def cursor(self):
        """
        Encapsulation function
        :return: cursor: An area in database memory that is dedicated to storing the last SQL statement
        """
        return self._cursor

    @property
    def connection(self):
        """
        Encapsulation function
        :return: connection: Connection string for getting access to the database
        """
        return self._connection

    @cursor.setter
    def cursor(self, cursor):
        """
        Function for "safety" changing of variable
        :param cursor: An area in database memory that is dedicated to storing the last SQL statement
        :return: cursor: Changed value of "cursor"
        """
        self._cursor = cursor

    @connection.setter
    def connection(self, connection):
        """
        Function for "safety" changing of variable
        :param connection: Connection string for getting access to the database
        :return: connection: Changed value of "connection"
        """
        self._connection = connection

    def connect_db(self) -> None:
        """
        Function connect to the database for some activities
        """
        path = os.path.abspath(os.path.join('..', 'savings', 'database', f'{self.name}.db'))
        self.connection = sqlite3.connect(path)
        self.cursor = self.connection.cursor()


class TableInDb(DataBase):

    def __init__(self, table_title: str, database_name: str) -> None:
        """
        Function initiate the new object from the table
        :param table_title:  title
        :param database_name: Database title
        """
        super().__init__(database_name)
        self.table_title = table_title

    def crt_new_table_and_connect_db(self, table_params: dict) -> None:
        """
        Function create the new table and add the columns inside
        :param table_params: Dict with the new column titles for the table
        """
        self.connect_db()
        cnt = 0
        print(self.table_title, table_params)
        for i_param, i_type in table_params.items():
            if cnt == 0:
                cnt += 1
                self.cursor.execute(f''' CREATE TABLE IF NOT EXISTS {self.table_title}({i_param} {i_type})''')
                print(f'New table {self.table_title} and new column {i_param} with type {i_type} successfully added')
            else:
                self.add_column({i_param: i_type})
        self.connection.commit()
        self.cursor.close()

    def add_column(self, table_params: dict) -> None:
        """
        Function add new columns in the table
        :param table_params: Dict with the new column titles for the table
        """
        self.connect_db()
        for i_param, i_type in table_params.items():
            try:
                self.cursor.execute(f''' ALTER TABLE {self.table_title} ADD COLUMN {i_param} {i_type}''')
            except sqlite3.OperationalError:
                get_warning_log(user='-', message=f'Duplicate column {i_param}', func_name= self.add_column.__name__,
                                func_path=abspath(__file__))
            else:
                print(f'New column {i_param} with type {i_type} successfully added')
        self.connection.commit()
        self.cursor.close()

    def check_data_in_table(self, param: str, value: (str, int)):
        result = self.cursor.execute(f'SELECT * FROM {self.table_title} WHERE {param}={value}')
        return result.fetchone() is None

    def insert_data(self, info: tuple) -> None:
        """
        Function create the new string in the table and paste data in each column
        :param info: Tuple with values for the new string in the table
        """
        self.connect_db()
        cols = tuple(i_param[1] for i_param in self.cursor.execute(f'PRAGMA table_info ({self.table_title});'))
        values = list(map(lambda num: '?, ' if num != len(cols) - 1 else '?', range(len(cols))))
        values = ''.join(values)

        try:
            self.cursor.execute(f'INSERT INTO {self.table_title}{cols} VALUES({values});', info)
        except sqlite3.DatabaseError as error:
            logger.exception(f'{error}')
        else:
            get_warning_log(user='', message=f'New data were added', func_name=self.insert_data.__name__,
                            func_path=abspath(__file__))
        self.connection.commit()
        self.cursor.close()

    # def change_data(self, id_param: str, value_id: (str, int), param_for_change: str, value_for_change: Any) -> None:
    #     self.connect_db()
    #     self.cursor.execute(f'UPDATE {self.table_title} Set {param_for_change} = ? '
    #                         f'WHERE {id_param} = ?', (value_for_change, value_id))
    #     self.connection.commit()
    #     self.cursor.close()

    def change_few_data(self, param: str, value: (str, int), data: dict) -> None:
        """
        Function change the values in the table according to requested parameters

        :param param: Column title for searching in the table
        :param value: Value for column "param"
        :param data: Dict with data for changing values in the table ({Column title : Value for this column}).
        """
        self.connect_db()
        for i_key, i_value in data.items():
            self.cursor.execute(f'UPDATE {self.table_title} Set {i_key} = ?'
                                f'WHERE {param} = ?', (i_value, value))
        self.connection.commit()
        self.cursor.close()

    def get_table(self, type_returned_data: str, param: str = None, value: str | int = None, user_id: int = None,
                  last_string: bool = None, param_2: str = None, value_2: str | int = None) -> List[dict] | Dict:
        """
        Function get the table from database according to requested parameters

        :param type_returned_data:
        :param param: Column title for searching in the table
        :param value: Value for column "id_param"
        :param user_id: UserID in the Bot
        :param last_string: Bool state for getting last string from the table
        :param param_2: 2nd Title of column for search in the table
        :param value_2: Value for column "param_2"

        :return: all_info: Received table or string from this table
        """
        self.connect_db()
        if not value and not user_id:
            self.cursor.execute(f'SELECT * FROM {self.table_title}')
        elif param_2 and value_2:
            self.cursor.execute(f'SELECT * FROM {self.table_title} WHERE {param} = {value} '
                                f'AND {param_2} = {value_2}')
        elif not user_id:
            self.cursor.execute(f'SELECT * FROM {self.table_title} WHERE {param} = "{value}"')
        elif not value:
            self.cursor.execute(f'SELECT * FROM {self.table_title} WHERE ID = {user_id}')
        else:
            self.cursor.execute(f'SELECT * FROM {self.table_title} WHERE {param} = {value} '
                                f'AND ID = {user_id}')
        result = self.cursor.fetchall()
        columns = tuple(i_param[1] for i_param in self.cursor.execute(f'PRAGMA table_info ({self.table_title});'))
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

    # def get_data(self, id_param: str, value: (str, int)) -> Any:
    #     self.connect_db()
    #     self.cursor.execute(f'SELECT * FROM {self.table_title} '
    #                         f'WHERE {id_param} = {value}')
    #     result = self.cursor.fetchall()
    #     self.cursor.close()
    #     return result[len(result) - 1]

    # def get_last_string(self) -> Any:
    #     """
    #     Function get the last string from the table
    #     :return: result: last string from the table
    #     """
    #     self.connect_db()
    #     self.cursor.execute(f''' SELECT * FROM {self.table_title};''')
    #     result = self.cursor.fetchall()
    #     self.cursor.close()
    #     return result[len(result) - 1]

    def delete_data(self, column_name: str, value: (str, int)) -> None:
        """
        Function delete the data from the table according to requested parameters and values
        :param column_name: Column title for searching in the table
        :param value: Value for column "id_param"
        """
        self.connect_db()
        self.cursor.execute(f"DELETE FROM {self.table_title} WHERE {column_name}='{value}';")
        self.connection.commit()
        self.cursor.close()

    # def download_csv(self) -> None:
    #     """
    #     Function download the csv format of table from database
    #     """
    #     self.connect_db()
    #     self.cursor.execute(f''' SELECT * FROM {self.table_title};''')
    #     with open('output.csv', 'w') as out_csv_file:
    #         csv_out = csv.writer(out_csv_file)
    #         # write header
    #         csv_out.writerow([d[0] for d in self.cursor.description])
    #         # write data
    #         for result in self.cursor:
    #             csv_out.writerow(result)
    #     self.cursor.close()
    #
    # def print_table(self) -> None:
    #     self.connect_db()
    #     self.cursor.execute(f''' SELECT * FROM {self.table_title};''')
    #     for i_param in self.cursor.execute(f'PRAGMA table_info ({self.table_title})'):
    #         print('|{: ^15}|'.format(i_param[1].upper()), end=' ')
    #     self.cursor.execute(f''' SELECT * FROM {self.table_title};''')
    #     for i_record in self.cursor.fetchall():
    #         for i_data in i_record:
    #             print('|{: ^15}|'.format(i_data), end=' ')
    #     self.cursor.close()
    #
    # def return_table(self) -> None:
    #     self.connect_db()
    #     # self.cursor.execute(f''' SELECT * FROM {self.table_title};''')
    #     # print(f'\n\tTable - "{self.table_title}" of database - "{self.name}":')
    #     for i_param in self.cursor.execute(f'PRAGMA table_info ({self.table_title})'):
    #         print('|{: ^15}|\n'.format(i_param[1].upper()), end=' ')
    #     self.cursor.execute(f''' SELECT * FROM {self.table_title};''')
    #     for i_record in self.cursor.fetchall():
    #         for i_data in i_record:
    #             print('|{: ^15}|\n'.format(i_data), end=' ')
    #     self.cursor.close()
    #     self.cursor.execute(f''' SELECT * FROM {self.table_title};''')
    #     return self.cursor.fetchall()

