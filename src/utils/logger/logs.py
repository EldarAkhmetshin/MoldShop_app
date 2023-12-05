#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import os
from loguru import logger


def get_info_log(user: str, message: str, func_name: str, func_path: str):
    """
    Функция записи INFO логов
    :param user: Имя пользователя
    :param func_path: Путь к исполняемому файлу
    :param message: Описание лога
    :param func_name: Имя исполняемой функции
    """
    try:
        logger.info('User: {: ^10} | Message: {: ^50} | Function: {: ^25} | Func_path: {: ^50}'.
                    format(user, message, func_name, func_path))
    except TypeError:
        logger.exception(f'User: {message} | Info log is not saved')


def get_warning_log(user: str, message: str, func_name: str, func_path: str):
    """
    Функция записи WARNING логов
    :param user: Имя пользователя
    :param func_path: Путь к исполняемому файлу
    :param message: Описание лога
    :param func_name: Имя исполняемой функции
    """
    try:
        logger.warning('User: {: ^10} | Message: {: ^50} | Function: {: ^25} | Func_path: {: ^50}'.
                       format(user, message, func_name, func_path))
    except TypeError:
        logger.exception(f'User: {message} | Warning log is not saved')

# @logger.catch(exception, *, level='ERROR', reraise=False, onerror=None, 
#               exclude=None, default=None, message="...")

def logger_add():
    """
    Функция создания файла для записей логов и настройки логов
    """
    path_temp_file = os.path.abspath(os.path.join('savings', 'logs', 'logs.log'))
    logger.add(path_temp_file, format="{time} {level} {message}", level="INFO", rotation="10000 KB", compression="zip")
