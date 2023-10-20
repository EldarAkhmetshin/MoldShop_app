import tkinter.ttk
from tkinter import Tk, Menu
from ttkthemes import ThemedStyle
from loguru import logger

from src.utils.gui.styles import define_styles
from src.utils.sql_database.new_tables import create_tables_in_db
from src.utils.logger.logs import logger_add
from src.utils.gui.main_app_funcs import App
from src.utils.gui.user_authorization_funcs import LogInApp
from src.global_values import user_data


def render_main_window():
    """
    Рендер основного окна приложения
    """
    # Создание окна приложения
    window = Tk()
    window.geometry('700x75')
    style = ThemedStyle(window)
    style.set_theme('radiance')
    define_styles()
    # Создание виджета с выпадающими списками команд, который находится под строкой заголовка вверху
    menu = Menu(window)
    window.config(menu=menu)
    help_menu = Menu(menu, tearoff=0)
    help_menu.add_command(label='Помощь', state='disabled')
    help_menu.add_command(label='О программе')
    menu.add_cascade(label='Справка', menu=help_menu)
    # Создание экземпляра класса осннового окна приложения и рендер конйнеров с виджетами
    app = App()
    app.render_widgets_main_menu()
    # Запуск работы окна приложения
    window.mainloop()


def log_in_app():
    """
    Рендер окна для авторизации пользователя
    """
    window = Tk()
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
    log_in_app()
    if user_data.get('access'):
        render_main_window()
