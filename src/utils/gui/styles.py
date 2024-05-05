#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from tkinter import *
from tkinter import ttk


def define_styles():
    """
    Функция для задания стилей определённым виджетам приложения
    """
    style = ttk.Style()

    style.configure(style='Regular.TLabel',
                    foreground='grey20',
                    anchor=N,
                    font=('Arial', '9', 'normal'))

    style.configure(style='Toolbar.TLabel',
                    anchor=N,
                    font=('Arial', '9', 'normal'))

    style.configure(style='Title.TLabel',
                    foreground='grey20',
                    anchor=N,
                    font=('Arial', '16', 'bold'))

    style.configure(style='Regular.TEntry',
                    foreground='grey20',
                    anchor=N,
                    font=('Arial', '9', 'normal'))

    style.configure(style='Treeview',
                    foreground='grey20',
                    font=('Arial', '11', 'normal'))

    style.configure(style='Menu.TButton', width=40, height=30, relief=RIDGE, compound=LEFT,
                    foreground='grey20',
                    anchor=N,
                    font=('Arial', '12', 'normal'))

    style.configure(style='Regular.TButton', width=10,
                    foreground='grey20',
                    anchor=N,
                    font=('Arial', '10', 'normal'))

    style.configure(style='Green.TButton',
                    width=11,
                    background='darkseagreen',
                    foreground='grey20',
                    anchor=N,
                    font=('Arial', '10', 'normal'))

    style.configure(style='Yellow.TButton',
                    width=11,
                    background='chartreuse',
                    foreground='grey20',
                    anchor=N,
                    font=('Arial', '10', 'normal'))

    style.configure(style='Coral.TButton',
                    width=11,
                    background='coral',
                    foreground='grey20',
                    anchor=N,
                    font=('Arial', '10', 'normal'))

    style.configure(style='Gold.TButton',
                    width=13,
                    background='gold',
                    foreground='grey20',
                    anchor=N,
                    font=('Arial', '10', 'normal'))

    style.configure(style='GreenToolbar.TButton',
                    background='chartreuse',
                    anchor=N)

    style.configure(style='RedToolbar.TButton',
                    background='coral',
                    anchor=N)
