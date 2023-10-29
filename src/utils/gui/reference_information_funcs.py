#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import os
import tkinter
from os.path import abspath
from tkinter import *
from tkhtmlview import HTMLLabel
from tkinter import ttk
from PIL import Image, ImageTk
from typing import Callable

from src.global_values import user_data
from src.utils.logger.logs import get_info_log
from src.data import user_rights


def check_user_rigths() -> str:
    define_answer: Callable = lambda: 'Да' if user_data.get(name) == 'True' else 'Нет'
    result = ''
    for name, description in user_rights.items():
        result = f'{result}\n\t{description}: {define_answer()}'
    return result


class ReferenceInfo(tkinter.Toplevel):
    """
    Класс представляет набор функций для вывода справочной информации о приложении
    """

    def __init__(self, app_info: bool = None):
        """
        Создание переменных
        :param app_info: Булево значение, принимающее значение True, когда необходимо вывести инфо о приложении
        """
        self.frame_additional = None
        self.app_info = app_info
        self.frame_header = None
        self.frame_body = None
        self.frame_bottom = None
        self.image_logo = Image.open(os.path.abspath(os.path.join('pics', 'company_logo.png'))) \
            .resize((150, 70))
        self.image_logo_pil = ImageTk.PhotoImage(self.image_logo)
        super().__init__()
        self.init_gui()

    def init_gui(self):
        """
        Инициация окна приложения и контенера для размещения виджетов
        """
        self.focus_set()
        self.frame_header = Frame(self, relief=RIDGE)
        self.frame_header.pack(side=TOP, padx=0)
        self.frame_body = Frame(self)
        self.frame_body.pack(fill=BOTH, expand=True)
        self.frame_additional = Frame(self)
        self.frame_additional.pack(fill=BOTH, expand=True)
        self.frame_bottom = Frame(self)
        self.frame_bottom.pack(fill=BOTH, expand=True)

    def render_widgets(self):
        """
        Функция рендера всех виджетов окна авторизации пользователя
        """
        if self.app_info:
            ttk.Label(self.frame_header, image=self.image_logo_pil).pack(side=TOP, padx=5, pady=5)
            ttk.Label(self.frame_body, text='\nПриложение: ArtPack MoldShop Manadgment'
                                            '\nВерсия: 1.0.0 от 08.11.23'
                                            f'\nПользователь: {user_data.get("user_name")}'
                                            f'\nПрава пользователя:'
                                            f'{check_user_rigths()}',
                      style='Regular.TLabel').pack(side=LEFT, padx=5, pady=5)
        else:
            HTMLLabel(self.frame_body, html=f"""
                        <h2>Справочная информация</h2>
                        <h3>Содержание</h3>
                        
                        <ul>
                          <li><a href='#section'>Загрузка нового BOM</a></li>
                          <li><a href="{os.path.abspath(os.path.join('pics', 'company_logo.png'))}">Взаимодействие со складом</a></li>
                        </ul>
                        <p>  **********  </p>
                        <h3 id='section'>Загрузка нового BOM</h3>
                        <p>
                          Чтобы привязать новый BOM к какой либо пресс-форме необходимо выполнить следующие действия:
                        </p>
                        <ul>
                          <li>1. Во вкладке "Перечень пресс-форм" нажать кнопку "Скачать шаблон";</li>
                          <li>2. В открывшемся окне выбрать нужный тип BOM (пресс-форма или горячий канал);</li>
                          <li>3. Cкачать актуальный шаблон Excel файла для заполнения информации;</li>
                          <li>4. Добавить информацию в скаченный Excel файл;</li>
                          <li>5. Сохранить файл в директорию своего компьютера, указав в его имени только номер пресс-формы. Чтобы загрузка произошла успешно необходимо убедиться, что пресс-форма под таким номером уже имеется в общем '
                                'перечне и название файла полностью совпадает с номером пресс-формы. <span>Например: название файла "1981-A.xlsx", а номер пресс-формы "1981-A"</span>;</li>
                          <li>6. Во вкладке "Перечень пресс-форм" нажать кнопку "Загрузить";</li>
                          <li>7. В открывшемся окне выбрать нужный тип BOM (пресс-форма или горячий канал);</li>
                          <li>8. При успешной загрузке данных откроется таблица в окне приложения</li>
                        <p>
                          После привязки нового BOM к пресс-форме. Excel файл больше не нужен. Вся информация будет хранится и обрабатываться в таблице базы данных.
                        </p>
                        <p>
                          Если нужно повторно загрузить BOM из Excel файла, в таком случае необходимо удалить старый BOM, нажав на кнопку "Удалить".
                        </p> 
                        </ul>              
            """).pack(pady=10, padx=10)

        get_info_log(user='-', message='Reference info widgets were rendered', func_name=self.render_widgets.__name__,
                     func_path=abspath(__file__))
        # Запуск работы окна приложения
        self.mainloop()
