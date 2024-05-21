#!/usr/bin/env python
# -*- coding: utf-8 -*- #
import os

mold_statuses_list = ['IN', 'OUT', 'IN SERVICE']
mold_statuses_dict = {'IN': '', 'OUT': '', 'IN SERVICE': ''}
part_statuses_list = ['В наличие', 'Отсутствующие', 'Меньше минимума', 'Наоборот']
info_messages = {
    'downloaded_bom': {'message_name': 'Уведомление о загрузке',
                       'message_body': 'Спецификация по номеру "{mold_number}" успешно внесена в систему'},
}
error_messages = {
    'not_downloaded_bom': {'message_name': 'Уведомление об ошибке',
                           'message_body': 'Спецификация по номеру "{mold_number}" НЕ загружена в систему'
                                           '\nУбедитесь, что п/ф с данным номером есть в общем перечне'
                                           '\n и что данный BOM не был загружен ранее'},
    'access_denied': {'message_name': 'Ошибка доступа',
                      'message_body': 'У Вас нет доступа. Для его предоставления обратитесь к администратору'}
}

columns_bom_parts_table = (
    '№ по парт листу', 'Наименование детали', 'Количество в форме', 'Описание', 'Доп. информация',
    'Изготовитель', 'Материал', 'Габариты', 'В наличие (новые), шт', 'В наличие (б/у), шт', 'Зона хранения',
    'Допустимый остаток, %', 'Вес, кг')
columns_sizes_bom_parts_table = {f'#{i}': 20 for i in range(1, len(columns_bom_parts_table) + 1)}

columns_molds_table = ('№ Формы', '№ горячего канала', 'Наименование', 'Название продукции',
                       'Год выпуска', 'Количество гнёзд', 'Производитель', 'Производитель г.к.', 'Статус',
                       'Местонахождение')
columns_sizes_molds_table = {f'#{i}': 20 for i in range(1, len(columns_molds_table) + 1)}

columns_molds_moving_history_table = ('Дата', 'Ответcтвенный', 'Номер пресс-формы',
                                      'Название проекта', 'Прошлый статус', 'Новый статус')
columns_sizes_moving_history_table = {f'#{i}': 20 for i in range(1, len(columns_molds_moving_history_table) + 1)}

columns_warehouse_table = ('Дата', 'Ответcтвенный', 'Номер пресс-формы', 'Номер запчасти',
                           'Имя запчасти', 'Тип запчасти', 'Количество')
columns_sizes_warehouse_table = {f'#{i}': 20 for i in range(1, len(columns_warehouse_table) + 1)}

columns_searching_results = ('Составляющая', 'Номер п/ф', 'Наименование элемента', 'Описание',
                             'Доп. информация', 'Наличие (новые)', 'Наличие (б/у)')
columns_sizes_searching_table = {f'#{i}': 20 for i in range(1, len(columns_searching_results) + 1)}
columns_purchased_parts = ('Номер закупки', 'Дата загрузки', 'Номер п/ф', 'Тип', 'Номер запчасти', 'Наименование',
                           'Описание', 'Закупленное кол-во', 'Статус', 'Комментарий')
columns_sizes_purchased_parts_table = {f'#{i}': 20 for i in range(1, len(columns_purchased_parts) + 1)}

columns_min_parts_excel_table = ('Номер п/ф', 'Тип', 'Номер запчасти', 'Наименование', 'Описание',
                                 'Кол-во в п/ф, шт', 'В наличие, шт', 'Необходимое кол-во, шт')
columns_customs_report_excel_table = ('Имя пресс-формы', 'Номер запчасти', 'Наименование', 'Описание запчасти',
                                      'Вес, кг', 'Габариты', 'Материал', 'Производитель / поставщик', 'Количество')

user_rights = {'stock_changing_in': 'Приём запчастей на склад',
               'stock_changing_out': 'Взятие запчастей со склада',
               'mold_status_changing': 'Перемещение пресс-форм (смена статуса)',
               'molds_and_boms_data_changing': 'Добавление и редактирование пресс-форм и элементов BOM',
               'attachments_changing': 'Редактирование вложенных файлов',
               'purchased_parts_uploading': 'Загрузка списка закупаемых запчастей'}
instructions = {'new_bom_uploading': f"""<h3>Загрузка нового BOM</h3>
                        <p>
                           <a href="{os.path.abspath(os.path.join('videos', 'New BOM uploading.mp4'))}">
                           Посмотреть видео</a>
                        <p>
                          Чтобы привязать новый BOM к какой либо пресс-форме необходимо выполнить следующие действия:
                        </p>
                        <ul>
                          <li>1. Во вкладке "Перечень пресс-форм" нажать кнопку "Скачать шаблон";</li>
                          <li>2. В открывшемся окне выбрать нужный тип BOM (пресс-форма или горячий канал);</li>
                          <li>3. Cкачать актуальный шаблон Excel файла для заполнения информации;</li>
                          <li>4. Добавить информацию в скаченный Excel файл;</li>
                          <li>5. Сохранить файл в директорию своего компьютера, указав в его имени только номер 
                          пресс-формы. 
                          Чтобы загрузка произошла успешно необходимо убедиться, что пресс-форма под таким номером 
                          уже имеется в общем
                                 перечне и название файла полностью совпадает с номером пресс-формы. <span>Например: 
                                 название файла "1981-A.xlsx", а номер пресс-формы "1981-A"</span>;</li>
                          <li>6. Во вкладке "Перечень пресс-форм" нажать кнопку "Загрузить";</li>
                          <li>7. В открывшемся окне выбрать нужный тип BOM (пресс-форма или горячий канал);</li>
                          <li>8. При успешной загрузке данных откроется таблица в окне приложения</li>
                        </ul>
                        <p>
                          После привязки нового BOM к пресс-форме. Excel файл больше не нужен. Вся информация будет 
                          хранится и обрабатываться в таблице базы данных.
                        </p>
                        <p>
                          Если нужно повторно загрузить BOM из Excel файла, в таком случае необходимо удалить 
                          старый BOM, нажав на кнопку "Удалить".
                        </p> 
                        """,
                'warehouse_operations': """<h3 id='section'>Взаимодействие со складом</h3>
                        <p>
                          Чтобы добавить или взять какую-либо запчасть со склада необходимо выполнить 
                          следующие действия:
                        </p>
                        <ul>
                          <li>1. Откройте необходимый BOM, найдя пресс-форму в общем перечне п/ф;</li>
                          <li>2. Выделить строку с нужным элементом в открытом BOM;</li>
                          <li>3. В зависимости от действия нажать кнопку "Приход" / "Расход";</li>
                          <li>4. В открывшемся окне заполнить 2 параметра. Тип детали ("Новая" / "Б/У") 
                          и количество;</li>
                          <li>5. Нажать "Применить";</li>
                        </ul>
                        <p>
                          В случае успешном проведении операции выведется сообщение с номером ячейки хранения 
                          выбранной запчасти.
                        </p> 
                        """,
                'molds_moving': """<h3 id='section'>Перемещение пресс-форм</h3>
                        <p>
                          Для изменения статуса / местоположения пресс-формы необходимо выполнить следующие действия:
                        </p>
                        <ul>
                          <li>1. В главном меню выбрать "Перемещение пресс-форм";</li>
                          <li>2. В области "Статус пресс-формы" нажать кнопку с местоположением, куда предполагается 
                          направить п/ф;</li>
                          <li>3. Отсканировать QR код закрепленный на п/ф. Информация зашитая в QR введётся в поле 
                          ввода открывшегося окна;</li>
                          <li>4. При успешной операции появится новая запись в таблице;</li>
                        </ul>
                        <p>
                          Расположение п/ф отображается в столбце "Статус". Существует 3 статуса: "IN" - п/ф 
                          в производстве, "IN SERVICE" - п/ф на обслуживании, "OUT" - п/ф хранится на складе.
                        </p> 
                        """,
                'app_possibilities': """<h3 id='section'>Основные возможности приложения</h3>
                        <ul>
                          <li>1. Централизованное хранение информации обо всех пресс-формах на балансе компании, а 
                          также спецификаций относящихся к этим п/ф;</li>
                          <li>2. Загрузка спецификации (BOM) в приложении по определённому шаблону из Excel файла;</li>
                          <li>3. Чтение и редактирование спецификаций, отображающихся в табличном виде;</li>
                          <li>4. Реализация функций склада для запчастей из спецификаций (приходы и расходы, ведение 
                          журнала истории);</li>
                          <li>5. Привязка различных файлов к п/ф и элементам спецификаций (BOM);</li>
                          <li>6. Просмотр, удаление, загрузка в локальную директорию пользователя 
                          прикреплённых файлов;</li>
                          <li>7. Экспорт какой-либо открытой таблицы в Excel файл;</li>
                          <li>8. Регистрация перемещений п/ф;</li>
                          <li>9. Поиск запчастей согласно введённым параметрам по загруженным спецификациям;</li>
                          <li>10. Автоматическая выгрузка в отдельный Excel файл запчастей, 
                          кол-во которых меньше необходимого минимума;</li>
                          <li>11. Верификация пользователя;</li>
                        </ul>""",
                'attachments': """<h3 id='section'>Работа с вложениями</h3>
                        <p>
                          Чтобы прикрепить файл какого-либо формата к п/ф или элементу из BOM необходимо выполнить 
                          следующие действия:
                        </p>
                        <ul>
                          <li>1. Выделить строку в таблице с нужным элементом в режиме просмотра перечня прес-форм 
                          или BOM;</li>
                          <li>2. Нажать соответствующую кнопку на панели инструментов в области "Вложения";</li>
                          <li>3. Выбрать файл из директории своего компьютера;</li>
                          <li>4. При успешной загрузке появится уведомление;</li>
                        </ul>
                        <p>
                          Чтобы просмотреть вложенные файлы к п/ф или элементу из BOM необходимо выполнить 
                          следующие действия:
                        </p>
                        <ul>
                          <li>1. Выделить строку в таблице с нужным элементом в режиме просмотра перечня прес-форм 
                          или BOM;</li>
                          <li>2. Нажать кнопку со скрепкой на панели инструментов в области "Вложения";</li>
                          <li>3. Если у элемента имеются вложенные файлы они отобразятся в открывшемся дополнительном 
                          окне;</li>
                          <li>4. Выбрать файл;</li>
                        </ul>
                        """,
                'purchased_spare_parts': """<h3 id='section'>Загрузка списка закупленных запчастей для отслеживания</h3>
                        <p>
                          Чтобы загрузить список закупленных запчастей для отслеживания применяется таблица
                          с выгрузкой по дефектации. Соответственно для корректной валидации не рекомендуется
                          удалять и переименовывать столбцы.
                          Идея заключается в том, что первоначально проводится дефектация. Создаётся список запчастей
                          для согласования с клиентом.
                          Этот список может быть отредактирован в плане удаления позиций, либо изменения 
                          требуемого количества.
                          Другие параметры редактировать НЕЛЬЗЯ! Это относится к номерам, наименованиям, 
                          именам столбцов. 
                        </p>
                        <p>
                          Новый элемент в таблице отслеживания отображается со статусом "Ожидается". Пользователь должен
                           изменить этот статус на "Принят на склад" по факту фактической приёмки. После чего 
                           кол-во данной запчасти будет автоматически изменено в соответствующем BOM (спецификации). 
                        </p>
                        """
                }
purchased_statuses = {'in_process': 'Ожидается',
                      'received': 'Принят на склад'}