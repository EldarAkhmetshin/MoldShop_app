# __`MoldShop Management App`__
## __Приложение для управления пресс-формами__
---
Предназначенно для оптимизации работы департамента обслуживания пресс-форм (п/ф).

## Возможности

- Централизованное хранение информации обо всех пресс-формах на балансе компании, а также спецификаций относящихся к этим п/ф
- Загрузка спецификации (BOM) в приложении по определённому шаблону из Excel файла
- Чтение и редактирование спецификаций, отображающихся в табличном виде
- Реализация функций склада для запчастей из спецификаций (приходы и расходы, ведение журнала истории) 
- Привязка различных файлов к п/ф и элементам спецификаций (BOM)
- Просмотр, удаление, загрузка в локальную директорию пользователя прикреплённых файлов
- Экспорт какой-либо открытой таблицы в Excel файл
- Регистрация перемещений п/ф
- Поиск запчастей согласно введённым параметрам по загруженным спецификациям
---
## Применяемый стек

- Python - На данном языке написан весь исполняемый код
- Tkinter - Библиотека для реализации графического интерфейса пользователя
- SQLIte3 - Используемая база данных для хранения всей информации
- HTML - Язык разметки, который применим для некоторых описаний в приложении

## Упаковка приложения в EXE файл

Установите в виртуальное окружение библиотеку pyinstaller

```sh
pip install pyinstaller
```

Запустите через консоль следующий скрипт:

```sh
pyinstaller --noconfirm --onedir --windowed --hidden-import "loguru" --hidden-import "ttkthemes" --add-data "D:/MoldShop_poject/savings;savings/" --add-data "D:/MoldShop_poject/pics;pics/" --add-data "D:/MoldShop_poject/src;src/" --hidden-import "tkinter.ttk" --hidden-import "tkinter" --hidden-import "pandas" --hidden-import "dotenv" --hidden-import "tkinter.messagebox" --hidden-import "tkinter.filedialog" --hidden-import "idlelib.tooltip" --hidden-import "pdf2image" "D:/MoldShop_poject/start.py" --icon "C:/Users/Ýëüäàð/Downloads/AP.ico" --name "MoldShop Managment"
```