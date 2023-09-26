from tkinter import *
from tkinter import ttk


def define_styles():
    print(ttk.Style().theme_names())
    style = ttk.Style()

    style.configure(style='Regular.TLabel',
                    foreground='grey20',
                    anchor=N,
                    font=('Arial', '9', 'normal'))

    style.configure(style='Toolbar.TLabel',
                    #foreground='grey20',
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

    style.configure(style='Regular.TButton',
                    foreground='grey20',
                    anchor=N,
                    font=('Arial', '10', 'normal'))

    style.configure(style='Green.TButton',
                    width=12,
                    background='darkseagreen',
                    foreground='grey20',
                    anchor=N,
                    font=('Arial', '10', 'normal'))

    style.configure(style='Yellow.TButton',
                    width=12,
                    background='chartreuse',
                    foreground='grey20',
                    anchor=N,
                    font=('Arial', '10', 'normal'))

    style.configure(style='Coral.TButton',
                    width=14,
                    background='coral',
                    foreground='grey20',
                    anchor=N,
                    font=('Arial', '10', 'normal'))

    style.configure(style='Gold.TButton',
                    width=14,
                    background='gold',
                    foreground='grey20',
                    anchor=N,
                    font=('Arial', '10', 'normal'))

    # style.map(style='Menu.TButton',
    #                  foreground=[('pressed', 'white'), ('active', 'blue')],
    #                  background=[('pressed', '!disabled', 'black'), ('active', 'white')])