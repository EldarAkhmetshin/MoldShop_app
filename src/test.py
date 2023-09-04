# import pandas as pd
# from openpyxl import load_workbook
#
# df = pd.DataFrame({'Name': ['Manchester City', 'Real Madrid', 'Liverpool',
#                             'FC Bayern München', 'FC Barcelona', 'Juventus'],
#                    'League': ['English Premier League (1)', 'Spain Primera Division (1)',
#                               'English Premier League (1)', 'German 1. Bundesliga (1)',
#                               'Spain Primera Division (1)', 'Italian Serie A (1)'],
#                    'TransferBudget': [176000000, 188500000, 90000000,
#                                       100000000, 180500000, 105000000]})
# df.to_excel('./teams.xlsx', sheet_name='Budgets', index=False)
#
# # salaries1 = pd.DataFrame({'Name': ['L. Messi', 'Cristiano Ronaldo', 'J. Oblak'],
# #                           'Salary': [560000, 220000, 125000]})
# #
# # salaries2 = pd.DataFrame({'Name': ['K. De Bruyne', 'Neymar Jr', 'R. Lewandowski'],
# #                           'Salary': [370000, 270000, 240000]})
# #
# # salaries3 = pd.DataFrame({'Name': ['Alisson', 'M. ter Stegen', 'M. Salah'],
# #                           'Salary': [160000, 260000, 250000]})
# #
# # salary_sheets = {'Group1': salaries1, 'Group2': salaries2, 'Group3': salaries3}
# # writer = pd.ExcelWriter('./salaries.xlsx', engine='xlsxwriter')
#
# # for sheet_name in salary_sheets.keys():
# #     salary_sheets[sheet_name].to_excel(writer, sheet_name=sheet_name, index=False)
#
# # writer.save()
#
# # top_players = pd.read_excel('./teams.xlsx')
# # print(top_players.head())
#
# cols = [0, 2]
#
# top_players = pd.read_excel('./teams.xlsx', index_col=1)
# # for i, k in top_players.items():
# #     for j in k:
# #         print(j)
#
#
# wb = load_workbook('./teams.xlsx')
# sheet = wb['Budgets']
# print(sheet['A4'].value)
#
# for cellObj in sheet['A2':'C15']:
#     for cell in cellObj:
#         print(cell.coordinate, cell.value)
#     print('--- END ---')


import os
from collections.abc import Iterable


def strings_count(directory: str) -> Iterable[tuple]:
    for root, dirs, files in os.walk(directory):
        for file in files:
            count = 0
            if os.path.join(root, file).endswith('.py'):
                curr_file = open(os.path.join(root, file), 'r', encoding='utf-8')
                for line in curr_file.readlines():
                    if not (line == '\n' or line.strip().startswith(('"', '#', "'"))):
                        count += 1
                yield os.path.join(root, file), count

cnt = 0
for element in strings_count(directory='..'):
    if not 'venv' in element[0]:
        print('Файл "{}": строк кода - {}'.format(element[0], element[1]))
        cnt += element[1]
print(cnt)
