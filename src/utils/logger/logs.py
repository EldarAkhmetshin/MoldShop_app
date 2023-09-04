import os
from loguru import logger


def get_info_log(user: str, message: str, func_name: str, func_path: str):
    """
    Function save INFO logs
    :param user:
    :param func_path:
    :param message: All information from Telegram about user
    :param func_name: Name of function which will call this func for writing log
    :return:
    """
    try:
        logger.info('User: {: ^10} | Message: {: ^50} | Function: {: ^25} | Func_path: {: ^50}'.
                    format(user, message, func_name, func_path))
    except TypeError:
        logger.exception(f'User: {message} | Info log is not saved')


def get_warning_log(user: str, message: str, func_name: str, func_path: str):
    """
    Function save WARNING logs
    :param user:
    :param func_path:
    :param message: All information from Telegram about user
    :param func_name: Name of function which will call this func for writing log
    :return:
    """
    try:
        logger.warning('User: {: ^10} | Message: {: ^50} | Function: {: ^25} | Func_path: {: ^50}'.
                       format(user, message, func_name, func_path))
    except TypeError:
        logger.exception(f'User: {message} | Warning log is not saved')


def logger_add():
    """
    Function create log file
    :return:
    """
    path_temp_file = os.path.abspath(os.path.join('..', 'savings', 'logs', 'logs.log'))
    logger.add(path_temp_file, format="{time} {level} {message}", level="INFO", rotation="10000 KB", compression="zip")
