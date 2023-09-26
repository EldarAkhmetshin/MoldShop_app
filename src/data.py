#!/usr/bin/env python
# -*- coding: utf-8 -*- #
mold_statuses_list = ['IN', 'OUT', 'IN SERVICE']
mold_statuses_dict = {'IN': '', 'OUT': '', 'IN SERVICE': ''}
part_statuses_list = ['В наличие', 'Отсутствующие', 'Меньше минимума']
info_messages = {
    'downloaded_bom': {'message_name': 'Уведомление о загрузке',
                       'message_body': 'Спецификация по номеру "{mold_number}" успешно внесена в систему'},
}
error_messages = {
    'not_downloaded_bom': {'message_name': 'Уведомление об ошибке',
                           'message_body': 'Спецификация по номеру "{mold_number}" НЕ загружена в систему'
                                           '\nУбедитесь, что п/ф с данным номером есть в общем перечне'},
}

columns_molds_moving_history_table = ('Дата', 'Отвественный', 'Номер пресс-формы',
                                      'Название проекта', 'Прошлый статус', 'Новый статус')
columns_sizes_moving_history_table = {f'#{i}': 20 for i in range(1, len(columns_molds_moving_history_table) + 1)}
