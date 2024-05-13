import os
from tkinter import Tk
from ttkthemes import ThemedStyle
from loguru import logger

from src.utils.gui.styles import define_styles
from src.utils.sql_database.new_tables import create_tables_in_db
from src.utils.logger.logs import logger_add
from src.main_app_funcs import App, create_menu_widgets
from src.utils.gui.user_authorization_funcs import LogInApp
from src.global_values import user_data


def render_main_window():
    """
    Рендер основного окна приложения
    """
    # Создание окна приложения
    window = Tk()
    window.state('zoomed')
    window.geometry('300x20')
    style = ThemedStyle(window)
    style.set_theme('radiance')
    window.iconbitmap(os.path.join('pics', 'artpack.ico'))
    define_styles()
    # Создание экземпляра класса окна приложения и рендер контейнеров с виджетами
    app = App()
    app.render_widgets_main_menu()
    create_menu_widgets(window, app)
    # Запуск работы окна приложения
    window.mainloop()


def log_in_app():
    """
    Рендер окна для авторизации пользователя
    """
    # check_passwords()
    window = Tk()
    window.iconbitmap(os.path.join('pics', 'artpack.ico'))
    style = ThemedStyle(window)
    style.set_theme('radiance')
    define_styles()
    window.geometry('300x220')
    window.resizable(False, False)
    app = LogInApp(window)
    window.bind('<Return>', app.on_pressed_key)
    app.render_widgets()


@logger.catch
def run():
    logger_add()
    create_tables_in_db()
    # add_columns_bom_table(columns={'WEIGHT': 'REAL'})
    # delete_titles_row_bom_table()
    log_in_app()
    if user_data.get('access'):
        render_main_window()
