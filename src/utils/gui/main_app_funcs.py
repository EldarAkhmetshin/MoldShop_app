#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import sqlite3
import tkinter
import os
from os.path import abspath

import PIL.ImageTk
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from pandas import DataFrame
from PIL import Image, ImageTk
from tkinter.ttk import Frame
from idlelib.tooltip import Hovertip
from typing import Callable

from src.global_values import user_data
from src.data import mold_statuses_dict, mold_statuses_list
from src.molds import get_data_from_excel_file, check_mold_number
from src.data import info_messages, error_messages
from src.utils.gui.bom_edition_funcs import EditedBOM
from src.utils.logger.logs import get_info_log
from src.utils.sql_database import table_funcs, new_tables
from src.utils.gui.new_mold_adding_funcs import NewMold
from src.utils.gui.mold_data_edition_funcs import EditedMold


def get_canvas(coordinate_x: int, coordinate_y: int, pad_x: int, pad_y: int,
               side: str, image: PIL.ImageTk.PhotoImage, canvas: tkinter.Canvas):
    """
    Рендер изображения в окне приложения.
    :param coordinate_x: Координата расположения по оси Х
    :param coordinate_y: Координата расположения по оси Y
    :param pad_x: Отступ виджета от границ фрейма по горизонтали
    :param pad_y: Отступ виджета от границ фрейма по вертикали
    :param side: Сторона позиционирования изображения
    :param image: Изображение в формате библиотеки PIL (для возможности работы с JPG файлами)
    :param canvas: Объект (изображение) в формате библиотеки tkinter
    :return:
    """
    canvas.create_image(coordinate_x, coordinate_y, anchor='nw', image=image)
    if side == 'left':
        canvas.pack(side=LEFT, padx=pad_x, pady=pad_y)
    elif side == 'right':
        canvas.pack(side=RIGHT, padx=pad_x, pady=pad_y)


class App(Frame):
    """
    Класс представляет набор функций для создания графического интерфейса основного окна приложения с помощью
    библиотеки Tkinter. А именно отрисовка / вывод различных изображений, таблиц, кнопок, полей ввода для обработки
    информации.
    """

    def __init__(self):
        """
        self.tree: Объект для вывода информации в табличном виде
        self.frame_header: Контейнер (прямоугольная область экрана) для отображения шапки приложения
        self.frame_main_widgets: Контейнер для отображения кнопок и полей ввода ниже шапки приложения
        self.frame_body: Контейнер для отображения основной информации (например: таблица)
        self.tracked_variable: Переменная для отслеживания записываемых данных в поле ввода
        self.sort_status: Текстовое значение указывающее на необходимость проведения сортировки перечня п/ф
        по определённому критерию ("IN"; "OUT"; "IN SERVICE").
        """
        super().__init__()
        self.part_number_entry_field = None
        self.all_molds_table_dict = None
        self.mold_number = None
        self.current_table = None
        self.mold_number_entry_field = None
        self.event = None
        self.tracked_variable = StringVar()
        # Объявление переменных изображений
        self.tracked_variable.trace("w", self.check_entry_field)
        self.image_logo = Image.open(os.path.abspath(os.path.join('..', 'pics', 'company_logo.png'))) \
            .resize((150, 70))
        self.image_logo_pil = ImageTk.PhotoImage(self.image_logo)
        self.image_body = Image.open(os.path.abspath(os.path.join('..', 'pics', 'main__picture.png'))) \
            .resize((800, 500))
        self.image_body_pil = ImageTk.PhotoImage(self.image_body)
        self.main_menu_icon = Image.open(os.path.abspath(os.path.join('..', 'pics', 'main_menu.png'))) \
            .resize((30, 30))
        self.main_menu_icon_pil = ImageTk.PhotoImage(self.main_menu_icon)
        self.image_mold = Image.open(os.path.abspath(os.path.join('..', 'pics', 'mold.png'))) \
            .resize((144, 120))
        self.image_mold_pil = ImageTk.PhotoImage(self.image_mold)
        self.image_spare_part = Image.open(os.path.abspath(os.path.join('..', 'pics', 'spare_parts.png'))) \
            .resize((144, 120))
        self.image_spare_part_pil = ImageTk.PhotoImage(self.image_spare_part)
        self.back_icon = Image.open(os.path.abspath(os.path.join('..', 'pics', 'back.png'))) \
            .resize((30, 30))
        self.back_icon_pil = ImageTk.PhotoImage(self.back_icon)
        self.plus_icon = Image.open(os.path.abspath(os.path.join('..', 'pics', 'plus.png'))) \
            .resize((30, 30))
        self.plus_icon_pil = ImageTk.PhotoImage(self.plus_icon)
        self.delete_icon = Image.open(os.path.abspath(os.path.join('..', 'pics', 'delete.png'))) \
            .resize((30, 30))
        self.delete_icon_pil = ImageTk.PhotoImage(self.delete_icon)
        self.edit_icon = Image.open(os.path.abspath(os.path.join('..', 'pics', 'edit.png'))) \
            .resize((30, 30))
        self.edit_icon_pil = ImageTk.PhotoImage(self.edit_icon)
        self.excel_icon = Image.open(os.path.abspath(os.path.join('..', 'pics', 'excel.png'))) \
            .resize((30, 30))
        self.excel_icon_pil = ImageTk.PhotoImage(self.excel_icon)
        self.info_icon = Image.open(os.path.abspath(os.path.join('..', 'pics', 'info.png'))) \
            .resize((30, 30))
        self.info_icon_pil = ImageTk.PhotoImage(self.info_icon)
        self.help_icon = Image.open(os.path.abspath(os.path.join('..', 'pics', 'help.png'))) \
            .resize((30, 30))
        self.help_icon_pil = ImageTk.PhotoImage(self.help_icon)
        self.new_attachment_icon = Image.open(os.path.abspath(os.path.join('..', 'pics', 'new_attachment.png'))) \
            .resize((30, 30))
        self.new_attachment_icon_pil = ImageTk.PhotoImage(self.new_attachment_icon)
        self.attachments_icon = Image.open(os.path.abspath(os.path.join('..', 'pics', 'attachments.png'))) \
            .resize((30, 30))
        self.attachments_icon_pil = ImageTk.PhotoImage(self.attachments_icon)
        # Объявление переменных будущих контейнеров для хранения виджетов
        self.tree = ttk.Treeview()
        self.frame_header = None
        self.frame_toolbar = None
        self.frame_main_widgets = None
        self.frame_body = None

        self.sort_status = None
        self.sorted_molds_data_tuple = None
        self.sorted_molds_data_dict = None
        self.molds_list_data = None

        self.key_two_func = None
        self.key_three_func = None
        self.key_four_func = None
        self.key_five_func = None

        self.init_gui()

    def init_gui(self):
        self.master.title('MoldShop Management')
        self.pack(fill=BOTH)

        self.frame_header = Frame(self, relief=RAISED)
        self.frame_header.pack()
        self.frame_main_widgets = Frame(self)
        self.frame_main_widgets.pack(anchor=N)
        self.frame_body = Frame(self)
        self.frame_body.pack(fill=X, expand=True)

    def check_entry_field(self, *args):
        """
        Проверка каждого введенного символа в поле ввода
        :param args:
        :return:
        """
        text = self.tracked_variable.get()
        if ';' in text:
            self.tracked_variable.set("")

    def open_file_and_download(self):
        """
        Функция загрузки спецификации пресс-формы (BOM) из Иксель файла формата xlsx в таблицу базы данных
        """
        # Открытие диалогового окна для выбора файла пользователем с локальной директории компьютера,
        # c дальнейшим извлечением пути к выбранному файлу в виде строки
        try:
            file_path = filedialog.askopenfile(
                filetypes=(('XLSX files', '*.xlsx'),)
            ).name
        except AttributeError:
            pass
        else:
            # Получение ишформации из Иксель файла типа xlsx
            column_names, rows_data = get_data_from_excel_file(file_path=file_path, work_sheet_name='BOM')
            file_path = file_path.split('/')
            mold_number = file_path[-1].replace('.xlsx', '')
            # Поиск соответствия по номеру пресс-формы в общем перечне
            if check_mold_number(mold_number):
                # Сохранение информации в базе данных
                new_tables.create_bom_for_new_mold(mold_number=mold_number, rows_data=rows_data)
                # Рендер окна приложения с новой загруженной информацией
                info_message = info_messages.get('downloaded_bom').get('message_body')
                self.mold_number = mold_number
                self.open_mold_bom(mold_number=mold_number)
                messagebox.showinfo(title=info_messages.get('downloaded_bom').get('message_name'),
                                    message=info_message.format(mold_number=mold_number))
            else:
                error_message = error_messages.get('not_downloaded_bom').get('message_body')
                messagebox.showerror(title=error_messages.get('not_downloaded_bom').get('message_name'),
                                     message=error_message.format(mold_number=mold_number))

    def save_excel_table(self):
        """
        Функция сохранения  открытой таблицы из окна приложения в Иксель файл формата xlsx
        """
        # Открытие диалогового окна для сохранения файла пользователем в локальной директории компьютера,
        # c дальнейшим извлечением пути к выбранному файлу в виде строки
        file_path = filedialog.asksaveasfilename(
            filetypes=(('XLSX files', '*.xlsx'),)
        )
        if file_path:
            file_path = file_path.replace('.xlsx', '')
            # Формирование Иксель файла типа xlsx
            table_length = len(self.current_table)
            saved_table = {}
            for num, column_name in enumerate(self.current_table[0]):
                saved_table[column_name] = tuple(self.current_table[i][num] for i in range(1, table_length))
            try:
                df = DataFrame(saved_table)
                df.to_excel(excel_writer=f'{file_path}.xlsx', sheet_name='Table', index=False)
            except Exception:
                messagebox.showerror(title='Уведомление об ошибке', message='Ошибка в записи файла.\nПовторите ещё раз, либо братитесь к администратору')
            else:
                messagebox.showinfo(title='Уведомление', message='Таблица успешно сохранена на Ваш компьютер')

    def render_header(self):
        """
        Рендер виджетов контейнера шапки окна приложения
        """
        # Рендер изображения
        canvas_logo = Canvas(self.frame_header, height=70, width=150)
        get_canvas(coordinate_x=0, coordinate_y=0, pad_x=2, pad_y=2, side='left',
                   image=self.image_logo_pil, canvas=canvas_logo)
        # Рендер надписи
        lbl1 = Label(self.frame_header, text="Mold Shop Management", width=100,
                     font=("Times", "20", "bold"), background="deepskyblue", foreground="gainsboro")
        lbl1.pack(side=TOP, padx=100, pady=20)

    def render_toolbar(self, back_func: Callable, add_row_func: Callable, edit_row_func: Callable,
                       delete_row_func: Callable):
        """
        Рендер виджетов панели иснтрументов
        :param back_func:
        :param add_row_func:
        :param edit_row_func:
        :param delete_row_func:
        :return:
        """
        # Объявление контейнеров
        self.frame_toolbar = Frame(self)
        self.frame_toolbar.pack(fill=X)
        toolbar = Frame(self.frame_toolbar, relief=RAISED)
        frame_toolbar_menu = Frame(toolbar, relief=RAISED)
        frame_toolbar_menu.pack(side=LEFT, padx=0)
        frame_toolbar_table = Frame(toolbar, relief=RAISED)
        frame_toolbar_table.pack(side=LEFT, padx=0)
        frame_toolbar_attachments = Frame(toolbar, relief=RAISED)
        frame_toolbar_attachments.pack(side=LEFT, padx=0)
        frame_toolbar_info = Frame(toolbar, relief=RAISED)
        frame_toolbar_info.pack(side=RIGHT, padx=0)
        # Объявление виджетов и их рендер
        line_symbols = '-----'
        Label(frame_toolbar_menu, text=f'Меню\n{line_symbols*2}').pack(side=TOP, padx=2, pady=1)
        menu_button = Button(frame_toolbar_menu, image=self.main_menu_icon_pil, highlightthickness=0, bd=0,
                             command=self.open_main_menu)
        menu_button.pack(side=LEFT, padx=3, pady=4)
        Hovertip(anchor_widget=menu_button, text='Главное меню', hover_delay=400)
        back_button = Button(frame_toolbar_menu, image=self.back_icon_pil, highlightthickness=0, bd=0,
                             command=back_func, highlightbackground='White')
        back_button.pack(side=LEFT, padx=3, pady=4)
        Hovertip(anchor_widget=back_button, text='Назад', hover_delay=400)

        Label(frame_toolbar_table, text=f'Таблица\n{line_symbols * 4}').pack(side=TOP, padx=2, pady=1)
        add_button = Button(frame_toolbar_table, image=self.plus_icon_pil, highlightthickness=0, bd=0,
                            command=add_row_func)
        add_button.pack(side=LEFT, padx=3, pady=4)
        Hovertip(anchor_widget=add_button, text='Добавить строку в таблицу', hover_delay=400)
        edit_button = Button(frame_toolbar_table, image=self.edit_icon_pil, highlightthickness=0, bd=0,
                             command=edit_row_func)
        edit_button.pack(side=LEFT, padx=3, pady=4)
        Hovertip(anchor_widget=edit_button, text='Редактировать строку', hover_delay=400)
        delete_button = Button(frame_toolbar_table, image=self.delete_icon_pil, highlightthickness=0, bd=0,
                               command=delete_row_func)
        delete_button.pack(side=LEFT, padx=3, pady=4)
        Hovertip(anchor_widget=delete_button, text='Удалить строку', hover_delay=400)
        download_excel_button = Button(frame_toolbar_table, image=self.excel_icon_pil, highlightthickness=0, bd=0,
                                       command=self.save_excel_table)
        download_excel_button.pack(side=LEFT, padx=3, pady=4)
        Hovertip(anchor_widget=download_excel_button, text='Выгрузить таблицу в Excel файл', hover_delay=400)

        Label(frame_toolbar_attachments, text=f'Вложения\n{line_symbols*2}').pack(side=TOP, padx=2, pady=1)
        new_attachment_button = Button(frame_toolbar_attachments, image=self.new_attachment_icon_pil,
                                       highlightthickness=0, bd=0,
                                       command=self.open_main_menu)
        new_attachment_button.pack(side=LEFT, padx=3, pady=4)
        Hovertip(anchor_widget=new_attachment_button, text='Прикрепить изображение / документ', hover_delay=400)
        open_attacments_button = Button(frame_toolbar_attachments, image=self.attachments_icon_pil,
                                        highlightthickness=0, bd=0,
                                        command=self.open_main_menu)
        open_attacments_button.pack(side=LEFT, padx=3, pady=4)
        Hovertip(anchor_widget=open_attacments_button, text='Просмотреть вложения', hover_delay=400)

        Label(frame_toolbar_info, text=f'Справка\n{line_symbols*2}').pack(side=TOP, padx=2, pady=1)
        Button(frame_toolbar_info, image=self.info_icon_pil, highlightthickness=0, bd=0,
               command=self.open_main_menu).pack(side=LEFT, padx=3, pady=4)
        Button(frame_toolbar_info, image=self.help_icon_pil,
               highlightthickness=0, bd=0, command=self.open_main_menu).pack(side=LEFT, padx=3, pady=4)

        toolbar.pack(side=TOP, fill=X)

    def render_main_body(self):
        """
        Рендер виджетов контейнера "body" окна приложения в главном меню
        :return:
        """
        canvas_body = Canvas(self.frame_body, height=500, width=800)
        get_canvas(coordinate_x=0, coordinate_y=0, pad_x=200, pad_y=20, side='right',
                   image=self.image_body_pil, canvas=canvas_body)

    def render_button(self, frame, text: str, column: int, row: int, command=None, arg_1=None, arg_2=None):
        btn = Button(
            frame, text=text, background='white',
            width=30, font=('Times', '12', 'bold'),
            command=lambda: command(arg_1, arg_2)
        )
        btn.grid(padx=45, pady=20, column=column, row=row)

    def render_widgets_main_menu(self):
        btn_molds_list = Button(
            self.frame_main_widgets, text='Перечень пресс-форм', background='white', width=30, height=2,
            relief=RIDGE, font=('Times', '13', 'bold'),
            command=lambda: self.get_molds_data()
        )
        btn_molds_list.grid(padx=30, pady=15, column=5, row=2)

        btn_scan_mode = Button(
            self.frame_main_widgets,
            text='Режим сканирования запчастей', background='white',
            width=30, height=2, relief=RIDGE, font=('Times', '13', 'bold'),
            # command=calculate_bmi
        )
        btn_scan_mode.grid(padx=30, pady=15, column=8, row=2)

        btn_search_mode = Button(
            self.frame_main_widgets,
            text='Поиск', background='white',
            width=30, height=2, relief=RIDGE, font=('Times', '13', 'bold'),
            # command=calculate_bmi
        )
        btn_search_mode.grid(padx=30, pady=15, column=15, row=2)

        btn_necessary_parts_report = Button(
            self.frame_main_widgets,
            text='Дефектация', background='white',
            width=30, height=2, relief=RIDGE, font=('Times', '13', 'bold'),
            # command=calculate_bmi
        )
        btn_necessary_parts_report.grid(padx=30, pady=15, column=5, row=3)

        btn_ordered_parts = Button(
            self.frame_main_widgets,
            text='Отслеживание поставок запчастей', background='white',
            width=30, height=2, relief=RIDGE, font=('Times', '13', 'bold'),
            # command=calculate_bmi
        )
        btn_ordered_parts.grid(padx=30, pady=15, column=8, row=3)

        btn_help_mode = Button(
            self.frame_main_widgets,
            text='Справка', background='white',
            width=30, height=2, relief=RIDGE, font=('Times', '13', 'bold'),
        )
        btn_help_mode.grid(padx=30, pady=15, column=15, row=3)

    def open_main_menu(self):
        """
        Рендер главного меню приложения
        """
        # Очистка контйнеров от старых виджетов
        self.tree.pack_forget()
        self.frame_main_widgets.pack_forget()
        self.frame_body.pack_forget()
        self.sort_status = None
        if self.frame_toolbar:
            self.frame_toolbar.pack_forget()
        self.remove_listeners()
        # Обновление контейнеров
        self.frame_header = Frame(self, relief=RAISED)
        self.frame_header.pack()
        self.frame_main_widgets = Frame(self)
        self.frame_main_widgets.pack(anchor=N)
        self.frame_body = Frame(self)
        self.frame_body.pack(fill=BOTH, expand=True)
        # Рендеров виджетов главного меню
        self.render_header()
        self.render_widgets_main_menu()
        self.render_main_body()

    def render_widgets_molds_list(self):
        """
        Функция рендера всех виджетов окна приложения в режиме просмотра перечня всех пресс-форм
        """
        # Очистка окна
        self.frame_header.pack_forget()
        # Рендер панели инструментов
        self.render_toolbar(back_func=self.open_main_menu, add_row_func=self.render_new_mold_window,
                            edit_row_func=self.render_mold_edition_window,
                            delete_row_func=self.delete_selected_table_row)
        # Объявление основного и вложенных контейнеров для виджетов
        self.frame_main_widgets = Frame(self, relief=RAISED)
        self.frame_main_widgets.pack(fill=X)
        main_sub_frame = Frame(self.frame_main_widgets)
        main_sub_frame.pack(side=LEFT, pady=2, padx=2)
        picture_subframe = Frame(self.frame_main_widgets)
        picture_subframe.pack(side=RIGHT, pady=2, padx=2)
        title_frame = Frame(main_sub_frame)
        title_frame.pack(side=TOP, padx=4)
        bom_frame = LabelFrame(main_sub_frame, text='BOM')
        bom_frame.pack(side=LEFT, padx=10, pady=1)
        sort_frame = LabelFrame(main_sub_frame, text='Сортировка')
        sort_frame.pack(side=LEFT, padx=0, pady=1)
        # Рендер виджетов
        (Label(title_frame, text=f'{" " * 50}Сводный перечень п/ф на балансе компании', font=('Times', '16', 'bold'))
         .pack(side=TOP, padx=4, pady=2))
        Label(title_frame, text=f'{" " * 65}*********').pack(side=TOP, padx=3, pady=2)
        Label(bom_frame, text='Введите номер пресс-формы:').pack(side=LEFT, padx=6, pady=5)

        self.mold_number_entry_field = Entry(bom_frame, font=('Times', '11', 'normal'),
                                             textvariable=self.tracked_variable)
        self.mold_number_entry_field.pack(side=LEFT, padx=6, pady=5)

        btn_bom = Button(
            bom_frame, text='Открыть', background='white',
            width=14, font=('Times', '11', 'normal'),
            command=lambda: self.open_mold_bom(mold_number=self.mold_number_entry_field.get())
        )
        btn_bom.pack(side=LEFT, padx=6, pady=5)

        btn_download_bom = Button(
            bom_frame, text='Загрузить', background='white',
            width=14, font=('Times', '11', 'normal'),
            command=self.open_file_and_download
        )
        btn_download_bom.pack(padx=6, pady=5, side=LEFT)
        Hovertip(btn_download_bom,
                 'Для загрузки в систему нового BOM (спецификации) используйте шаблон таблицы "mold_bom_template.xlsx" '
                 '\nиз папки "templates". '
                 '\nЧтобы загрузка произошла успешно убедитесь, что пресс-форма под таким номером уже имеется в общем '
                 '\nперечне и название файла полностью совпадает с номером пресс-формы. Например: название файла'
                 '\n"1981-A.xlsx" и номер пресс-формы "1981-A"',
                 hover_delay=400)

        Button(
            sort_frame, text='Все п/ф', background='darkseagreen',
            width=14, font=('Times', '11', 'normal'),
            command=lambda: self.get_molds_data(sort_status=False)
        ).pack(padx=6, pady=5, side=LEFT)

        Button(
            sort_frame, text='Активные п/ф', background='chartreuse',
            width=14, font=('Times', '11', 'normal'),
            command=lambda: self.get_molds_data(sort_status='IN')
        ).pack(padx=6, pady=5, side=LEFT)

        Button(
            sort_frame, text='Не активные п/ф', background='coral',
            width=14, font=('Times', '11', 'normal'),
            command=lambda: self.get_molds_data(sort_status='OUT')
        ).pack(padx=6, pady=5, side=LEFT)

        Button(
            sort_frame, text='П/ф на ТО2', background='gold',
            width=14, font=('Times', '11', 'normal'),
            command=lambda: self.get_molds_data(sort_status='IN SERVICE')
        ).pack(padx=6, pady=5, side=LEFT)

        canvas = Canvas(picture_subframe, height=120, width=250)
        canvas.create_image(100, 5, anchor='nw', image=self.image_mold_pil)
        canvas.pack(side=RIGHT, pady=1)

        get_info_log(user=user_data.get('user_name'), message='Mold list widgets were rendered',
                     func_name=self.render_widgets_molds_list.__name__, func_path=abspath(__file__))

    def render_widgets_selected_bom(self):
        """
        Функция рендера всех виджетов окна приложения в режиме просмотра BOM (спецификации) пресс-формы
        """
        # Рендер панели инструментов
        self.render_toolbar(back_func=self.get_molds_data, add_row_func=self.get_molds_data,
                            edit_row_func=self.render_bom_edition_window,
                            delete_row_func=self.delete_selected_table_row)
        # Объявление основного и вложенных контейнеров для виджетов
        self.frame_main_widgets = Frame(self, relief=RAISED)
        self.frame_main_widgets.pack(fill=X)
        main_sub_frame = Frame(self.frame_main_widgets)
        main_sub_frame.pack(fill=X, side=LEFT, pady=2, padx=2)
        picture_subframe = Frame(self.frame_main_widgets)
        picture_subframe.pack(side=RIGHT, pady=2, padx=2)
        title_frame = Frame(main_sub_frame)
        title_frame.pack(fill=BOTH, expand=True)
        description_frame = Frame(main_sub_frame)
        description_frame.pack(fill=BOTH, expand=True)
        search_frame = LabelFrame(main_sub_frame, text='Поиск')
        search_frame.pack(side=LEFT, padx=10, pady=1)
        sort_frame = LabelFrame(main_sub_frame, text='Сортировка')
        sort_frame.pack(side=LEFT, padx=0, pady=1)
        # Рендер виджетов
        molds_data = table_funcs.TableInDb('All_molds_data', 'Database')
        mold_info = molds_data.get_table(type_returned_data='dict', param='MOLD_NUMBER', value=self.mold_number,
                                         last_string=True)
        (Label(title_frame, text=f'BOM для пресс-формы № {self.mold_number} ', font=('Times', '16', 'bold'))
         .pack(side=LEFT, padx=8, pady=4))
        Label(description_frame,
              text=f'Проект: {mold_info.get("MOLD_NAME")} | Год: {mold_info.get("RELEASE_YEAR")} | , '
                   f'Кол-во гнёзд: {mold_info.get("CAVITIES_QUANTITY")}').pack(side=LEFT, padx=8, pady=1)
        Label(search_frame, text='Введите название элемента:').pack(side=LEFT, padx=10, pady=5)

        self.part_number_entry_field = Entry(search_frame, font=('Times', '11', 'normal'),
                                             textvariable=self.tracked_variable)
        self.part_number_entry_field.pack(side=LEFT, padx=6, pady=5)

        btn_bom = Button(
            search_frame, text='Найти', background='white',
            width=14, font=('Times', '11', 'normal'),
            command=lambda: self.open_mold_bom(mold_number=self.part_number_entry_field.get())
        )
        btn_bom.pack(side=LEFT, padx=6, pady=5)

        btn_download_bom = Button(
            search_frame, text='Загрузить', background='white',
            width=14, font=('Times', '11', 'normal'),
            command=self.open_file_and_download
        )
        btn_download_bom.pack(padx=6, pady=5, side=LEFT)

        Button(
            sort_frame, text='Все', background='darkseagreen',
            width=14, font=('Times', '11', 'normal'),
            command=lambda: self.get_molds_data(sort_status=False)
        ).pack(padx=6, pady=5, side=LEFT)

        Button(
            sort_frame, text='В наличие', background='chartreuse',
            width=14, font=('Times', '11', 'normal'),
            command=lambda: self.get_molds_data(sort_status='IN')
        ).pack(padx=6, pady=5, side=LEFT)

        Button(
            sort_frame, text='Отсутствующие', background='coral',
            width=14, font=('Times', '11', 'normal'),
            command=lambda: self.get_molds_data(sort_status='OUT')
        ).pack(padx=6, pady=5, side=LEFT)

        Button(
            sort_frame, text='Меньше минимума', background='gold',
            width=16, font=('Times', '11', 'normal'),
            command=lambda: self.get_molds_data(sort_status='IN SERVICE')
        ).pack(padx=6, pady=5, side=LEFT)

        canvas = Canvas(picture_subframe, height=120, width=250)
        canvas.create_image(100, 5, anchor='nw', image=self.image_spare_part_pil)
        canvas.pack(side=RIGHT, pady=1)

    def on_clicked_or_pressed_table_row(self, event):
        """
        Обработчик события двойного нажатия мыши или клавиши Enter на выделеную строку таблицы
        :param event: Обрабатываемое событие
        """
        self.open_mold_bom()
        self.event = event

    def on_pressed_key_one(self, event):
        """
        Обработчик события нажатия клавиши 1
        :param event: Обрабатываемое событие
        """
        self.open_main_menu()

    def on_pressed_key_two(self, event):
        """
        Обработчик события нажатия клавиши 2
        :param event: Обрабатываемое событие
        """
        try:
            self.key_two_func()
        except TypeError:
            pass

    def on_pressed_key_three(self, event):
        """
        Обработчик события нажатия клавиши 3
        :param event: Обрабатываемое событие
        """
        try:
            self.key_three_func()
        except TypeError:
            pass

    def on_pressed_key_four(self, event):
        """
        Обработчик события нажатия клавиши 4
        :param event: Обрабатываемое событие
        """
        try:
            self.key_four_func()
        except TypeError:
            pass

    def on_pressed_key_five(self, event):
        """
        Обработчик события нажатия клавиши 5
        :param event: Обрабаьываемое событие
        """
        try:
            self.key_five_func()
        except TypeError:
            pass

    def render_table(self, columns_sizes: dict):
        """
        Вывод таблицы в отображаемом окне приложения на основе полученных данных, которые были предварительно
        загруженны из таблицы базы данных
        :param columns_sizes: Информация о размере каждого столбца таблицы
        """
        # определяем столбцы
        columns = self.current_table[0]
        # определяем таблицу
        self.tree = ttk.Treeview(columns=columns, show="headings")
        self.tree.pack(fill=BOTH, expand=1)
        # определяем заголовки
        for col_name in columns:
            self.tree.heading(col_name, text=col_name)
        # настраиваем столбцы
        for col_num, col_size in columns_sizes.items():
            self.tree.column(column=col_num, stretch=YES, width=col_size)
        # Добавление данных в отображаемую таблицу. Чтобы последняя добавленная информацию отображалась необходимо
        # прежде сделать реверсию массива данных
        reversed_data = list(reversed(self.current_table[1:]))
        for row in reversed_data:
            self.tree.insert("", END, values=row)
        # # добавляем вертикальную прокрутку
        # scrollbar = ttk.Scrollbar(self.tree, orient=VERTICAL, command=self.tree.yview)
        # self.tree.configure(yscrollcommand=scrollbar.set)
        # # scrollbar.grid(row=0, column=1, sticky="ns")
        # scrollbar.pack(side=RIGHT)

    def get_row_number_in_table(self) -> int:
        """
        Данная функция преобразует полученный ID номер выделенной строки пользователем в таблице  в порядковый номер строки.
        В библиотеке Tkinter ID присваивается следующим образом: I001, I002, ..., I009, I00A, I00B, I00C, I00D, I00E, I00F,
        I010, I011, ..., I01A, I01B, I01C, I01D, I01E, I01F, I020, I021, ....
        Соответственно для корректного получения порядкового номера строки необходимо учесть числовые и буквенные итерации.
        :return: порядковый номер выделенной строки
        """

        tree_row_id = self.tree.focus().replace('I', '')
        if tree_row_id:
            cycle_number = int(tree_row_id[:-1])

            try:
                row_id = int(tree_row_id) - 1
            except ValueError:
                letter_values = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5}
                indicated_letter = tree_row_id[-1]
                cycle_number = int(tree_row_id[:-1])
                row_id = int(f'{cycle_number + 1}{letter_values.get(indicated_letter)}') - 1

            return row_id + cycle_number * 6

    def get_molds_data(self, sort_status: str | bool = None):
        """
        Функция вывода перечня всех пресс-форм в табличном виде в окне приложения
        :param sort_status: Текстовое значение указывающее на необходимость проведения сортировки перечня п/ф
            по определённому критерию ("IN"; "OUT"; "IN SERVICE").
        """
        # Выгрузка из базы данных перечня пресс-форм, сортировка и запись в переменные класса
        self.sort_molds()
        # Очистка области в окне приложения перед выводом новой таблицы
        if self.frame_toolbar:
            self.frame_toolbar.pack_forget()
        self.frame_main_widgets.pack_forget()
        self.frame_body.pack_forget()
        self.tree.pack_forget()
        if sort_status:
            self.sort_status = sort_status
            self.current_table = self.sorted_molds_data_tuple.get(sort_status)
        else:
            self.sort_status = None
        # Рендер кнопок для данного окна
        self.render_widgets_molds_list()
        # Определение размера столбцов таблицы
        columns_sizes = {'#1': 5, '#2': 10, '#3': 35, '#4': 25, '#5': 10, '#6': 10, '#7': 20, '#8': 20, '#9': 20,
                         '#10': 20}
        # Рендер таблицы
        self.render_table(columns_sizes=columns_sizes)
        # Объявление обработчиков событий на двойной клик мышью или клавиши Enter
        self.tree.bind('<Double-ButtonPress-1>', self.on_clicked_or_pressed_table_row)
        self.tree.bind('<Return>', self.on_clicked_or_pressed_table_row)
        # Объявление других обработчиков событий
        self.add_listeners(funk_two=self.open_main_menu, funk_three=self.render_new_mold_window,
                           funk_four=self.render_mold_edition_window)

    def add_listeners(self, funk_two: Callable, funk_three: Callable = None,
                      funk_four: Callable = None, funk_five: Callable = None):
        """
        Функция добавления обработчиков событий при нажатии клавиш клавиатуры
        :param funk_two: Вызываемая функция клавиши 2
        :param funk_three: Вызываемая функция клавиши 3
        :param funk_four: Вызываемая функция клавиши 4
        :param funk_five: Вызываемая функция клавиши 5
        """
        self.key_two_func = funk_two
        self.key_three_func = funk_three
        self.key_four_func = funk_four
        self.key_five_func = funk_five
        self.master.bind('1', self.on_pressed_key_one)
        self.master.bind('2', self.on_pressed_key_two)
        self.master.bind('3', self.on_pressed_key_three)
        self.master.bind('4', self.on_pressed_key_four)
        self.master.bind('5', self.on_pressed_key_five)

    def remove_listeners(self):
        """
        Функция удаления удаления обработчиков событий
        """
        for key in range(1, 6):
            self.master.unbind(f'{key}')

    def sort_molds(self):
        """
        Функция сортировки общего перечня пресс-форм в зависимости от её статуса и записи информации в переменные класса.
        Вызывается при открытие окна с перечнем п/ф. Функция необходима для минимизации количества вызовов базы данных.
        """
        # Перезапись переменных для обновления данных, которые будут получены из БД
        self.sorted_molds_data_tuple = {status: [] for status in mold_statuses_list}
        self.sorted_molds_data_dict = {status: [] for status in mold_statuses_list}
        # Выгрузка таблицы из БД
        molds_data = table_funcs.TableInDb('All_molds_data', 'Database')
        self.all_molds_table_dict = molds_data.get_table(type_returned_data='dict')
        self.molds_list_data = molds_data.get_table(type_returned_data='tuple')
        self.current_table = molds_data.get_table(type_returned_data='tuple')
        # Сортировка и запись в зависимости от статуса
        for num, mold_info in enumerate(self.all_molds_table_dict):
            if num == 0:
                for status in mold_statuses_list:
                    self.sorted_molds_data_dict.get(status).append(mold_info)
                    self.sorted_molds_data_tuple.get(status).append(self.molds_list_data[num])
            else:
                status = mold_info.get('STATUS')
                self.sorted_molds_data_dict.get(status).append(mold_info)
                self.sorted_molds_data_tuple.get(status).append(self.molds_list_data[num])

    def get_mold_number_by_selected_row(self) -> str:
        # Получения номера выделенной строки
        table_row_number = self.get_row_number_in_table()
        # Выгрузка информации из базы данных сводного перечня всех пресс-форм, чтобы
        # по номеру выделенной строки (table_row_number) в таблице определить номер пресс-формы (mold_number)
        # Так как выведенная таблица в окне приложения перевернутая,
        # необходимо сделать реверсию массива после выгрузки
        if self.sort_status:
            molds_table = self.sorted_molds_data_dict.get(self.sort_status)
        else:
            molds_list = table_funcs.TableInDb('All_molds_data', 'Database')
            molds_table = molds_list.get_table(type_returned_data='dict')
        reversed_molds_table = list(reversed(molds_table))
        # Получение номера пресс-форма из массива данных
        try:
            return reversed_molds_table[table_row_number].get('MOLD_NUMBER')
        except (TypeError, IndexError):
            pass

    def get_part_number_by_selected_row(self) -> str:
        # Получения номера выделенной строки
        table_row_number = self.get_row_number_in_table()
        # Выгрузка информации из базы данных сводного перечня всех пресс-форм, чтобы
        # по номеру выделенной строки (table_row_number) в таблице определить номер пресс-формы (mold_number)
        # Так как выведенная таблица в окне приложения перевернутая,
        # необходимо сделать реверсию массива после выгрузки
        if self.sort_status:
            bom_table = self.sorted_molds_data_dict.get(self.sort_status)
        else:
            bom = table_funcs.TableInDb(f'BOM_{self.mold_number}', 'Database')
            bom_table = bom.get_table(type_returned_data='dict')
        reversed_bom_table = list(reversed(bom_table))
        # Получение номера пресс-форма из массива данных
        try:
            return reversed_bom_table[table_row_number].get('NUMBER')
        except (TypeError, IndexError):
            pass

    def open_mold_bom(self, mold_number: str = None):
        """
        Функция для вывода спецификации (BOM) пресс-формы в табличном виде в окне приложения
        :param mold_number: Номер пресс-формы полученный из строки ввода
        """
        self.mold_number_entry_field.delete(0, END)
        if not mold_number:
            mold_number = self.get_mold_number_by_selected_row()

        try:
            # Выгрузка информации из базы данных
            self.mold_number = mold_number
            mold_bom = table_funcs.TableInDb(f'BOM_{mold_number}', 'Database')
            self.current_table = mold_bom.get_table(type_returned_data='tuple')
        except sqlite3.OperationalError:
            messagebox.showerror('Уведомление об ошибке', f'Спецификации по номеру "{mold_number}" не имеется')
        else:
            # Очистка области в окне приложения перед выводом новой таблицы
            self.tree.unbind("<Double-ButtonPress-1>")
            self.tree.unbind("<Return>")
            self.frame_toolbar.pack_forget()
            self.frame_main_widgets.pack_forget()
            self.tree.pack_forget()
            # Обновление обработчиков событий
            self.remove_listeners()
            self.add_listeners(funk_two=self.get_molds_data, funk_four=self.render_bom_edition_window)
            # Рендер кнопок для данного окна
            self.sort_status = None
            self.render_widgets_selected_bom()
            # Рендер таблицы
            columns_sizes = {'#1': 5, '#2': 10, '#3': 35, '#4': 25, '#5': 10, '#6': 10, '#7': 20, '#8': 20}
            self.render_table(columns_sizes=columns_sizes)

    def render_new_mold_window(self):
        """
        Рендер окна для ввода данных о новой пресс-форме
        """
        new_mold_app = NewMold()
        new_mold_app.title('New Mold Information')
        new_mold_app.resizable(False, False)
        new_mold_app.render_widgets()
        if new_mold_app.new_mold_information:
            self.tree.pack_forget()
            self.get_molds_data()

    def render_mold_edition_window(self):
        """
        Рендер окна для редактирования данных о пресс-форме
        """
        mold_number = self.mold_number_entry_field.get()
        if not mold_number:
            mold_number = self.get_mold_number_by_selected_row()

        if mold_number:

            try:
                # Выгрузка информации о пресс-форме из базы данных
                all_molds_data = table_funcs.TableInDb('All_molds_data', 'Database')
                mold_data = all_molds_data.get_table(type_returned_data='dict', param='MOLD_NUMBER',
                                                     value=mold_number, last_string=True)
            except (sqlite3.OperationalError, IndexError):
                messagebox.showerror('Уведомление об ошибке', f'Данных о пресс-форме "{mold_number}" не имеется')
            else:
                edited_mold_app = EditedMold(mold_data=mold_data)
                edited_mold_app.title('Mold Data Edition')
                edited_mold_app.resizable(False, False)
                edited_mold_app.render_widgets()
                if edited_mold_app.edited_mold_information:
                    self.tree.pack_forget()
                    self.get_molds_data()

    def render_bom_edition_window(self):
        """
        Рендер окна для редактирования данных о пресс-форме
        """
        part_number = self.part_number_entry_field.get()
        if not part_number:
            part_number = self.get_part_number_by_selected_row()

        if part_number:

            try:
                # Выгрузка информации о пресс-форме из базы данных
                bom = table_funcs.TableInDb(f'BOM_{self.mold_number}', 'Database')
                part_data = bom.get_table(type_returned_data='dict', param='NUMBER',
                                          value=part_number, last_string=True)
            except (sqlite3.OperationalError, IndexError):
                messagebox.showerror('Уведомление об ошибке', f'Данных о запчасти не имеется')
            else:
                edited_bom_app = EditedBOM(part_data=part_data, mold_number=self.mold_number)
                edited_bom_app.title('BOM Edition')
                edited_bom_app.resizable(False, False)
                edited_bom_app.render_widgets()
                if edited_bom_app.edited_part_data:
                    self.tree.pack_forget()
                    self.open_mold_bom(self.mold_number)

    def delete_selected_table_row(self):
        """
        Фнкция удаления строки из таблицы базы данных на основании выделенной строки
        """
        mold_number = self.get_mold_number_by_selected_row()
        molds_list = table_funcs.TableInDb('All_molds_data', 'Database')

        message = "Вы уверены, что хотите удалить данную строку"
        if messagebox.askyesno(title='Подтверждение', message=message, parent=self):
            try:
                molds_list.delete_data(column_name='MOLD_NUMBER', value=mold_number)
            except sqlite3.OperationalError:
                messagebox.showerror('Уведомление об ошибке', 'Ошибка удаления. Обратитесь к администратору.')
            else:
                messagebox.showinfo('Уведомление', 'Удаление успешно произведено!')
                self.tree.pack_forget()
                self.get_molds_data()

    def confirm_delete(self):
        message = "Вы уверены, что хотите удалить данную строку"
        if messagebox.askyesno(title='Подтверждение', message=message, parent=self):
            return True

