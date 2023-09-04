import time
from tkinter import Tk, Menu

from src.utils.sql_database.new_tables import create_tables_in_db
from src.utils.logger.logs import logger_add
from src.utils.gui.main_app_funcs import App
from src.utils.gui.user_authorization_funcs import LogInApp
from src.global_values import user_data


def render_main_window():
    """
    Рендер основного окна приложения
    :return:
    """
    # Создание окна приложения
    window = Tk()
    window.geometry('700x75')
    # Создание виджета с выпадающими списками команд, который находится под строкой заголовка вверху
    menu = Menu(window)
    window.config(menu=menu)
    help_menu = Menu(menu, tearoff=0)
    help_menu.add_command(label='Помощь', state='disabled')
    help_menu.add_command(label='О программе')
    menu.add_cascade(label='Справка', menu=help_menu)
    # Создание экземпляра класса осннового окна приложения и рендер конйнеров с виджетами
    app = App()
    app.render_header()
    app.render_widgets_main_menu()
    app.render_main_body()
    # Запуск работы окна приложения
    window.mainloop()


def log_in_app():
    """Рендер окна для авторизации пользователя
    :return:
    """
    window = Tk()
    window.geometry('300x220')
    window.resizable(False, False)
    app = LogInApp(window)
    window.bind('<Return>', app.on_pressed_key)
    app.render_widgets()


if __name__ == '__main__':
    logger_add()
    create_tables_in_db()
    log_in_app()
    if user_data.get('access'):
        render_main_window()
