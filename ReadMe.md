# [__`MoldShop Management App`__](https://www.artpackplastics.com/)

## __Приложение для управления пресс-формами__
---
Предназначено для оптимизации работы департамента обслуживания пресс-форм (п/ф). В нём заложен функционал аналогичный
PDM системе для обработки информации.

## Возможности

- Централизованное хранение информации обо всех пресс-формах на балансе компании, а также спецификаций относящихся к
  этим п/ф
- Загрузка спецификации (BOM) в приложение по определённому шаблону из Excel файла
- Чтение и редактирование спецификаций, отображающихся в табличном виде
- Реализация функций склада для запчастей из спецификаций (приходы и расходы, ведение журнала истории)
- Привязка различных файлов к п/ф и элементам спецификаций (BOM)
- Просмотр, удаление, загрузка в локальную директорию пользователя прикреплённых файлов
- Экспорт какой-либо открытой таблицы в Excel файл
- Регистрация перемещений п/ф
- Поиск запчастей согласно введённым параметрам по загруженным спецификациям
- Верификация пользователя
- Автоматическая выгрузка в отдельный Excel файл запчастей, кол-во которых меньше необходимого минимума

---

## Применяемый стек

- Python - На данном языке написан весь исполняемый код
- Tkinter - Библиотека для реализации графического интерфейса пользователя
- SQLIte3 - Используемая б/д для хранения всей информации
- Pandas и Openpyxl - Библиотеки для взаимодействия с Excel файлами
- HTML - Язык разметки, который применим для некоторых описаний в приложении

---

## Примечание для разработчика

Строка кода модуля внешней библиотеки виртуального окружения tkinter/ttk.py -> функции "def _tclobj_to_py(val)" -> 
"val = list(map(_convert_stringval, val))" должна быть закомментирована, 
иначе не будут открыты спецификации имена, которых могут быть приведены к int (К примеру 07865... или 6913_5),
по причине конвертации строкового значения в числовое, что в результате приводит к смене исходного значения.

---

## Запуск приложения из EXE файла

Установить в виртуальное окружение библиотеку pyinstaller

```sh
pip install pyinstaller
```

Запустить в терминале следующий скрипт (необходимо скорректировать некоторые ссылки, чтобы запустить на своём ПК):

```sh
pyinstaller --noconfirm --onedir --windowed --hidden-import "loguru" --hidden-import "tkhtmlview" --hidden-import "ttkthemes" --add-data "D:/MoldShop_poject/savings;savings/" --add-data "D:/MoldShop_poject/pics;pics/" --add-data "D:/MoldShop_poject/src;src/" --hidden-import "tkinter.ttk" --hidden-import "tkinter" --hidden-import "pandas" --hidden-import "dotenv" --hidden-import "tkinter.messagebox" --hidden-import "tkinter.filedialog" --hidden-import "idlelib.tooltip" "D:/MoldShop_poject/start.py" --icon "D:/MoldShop_poject/pics/artpack.ico" --name "MoldShop Management"
```

```sh
pyinstaller --noconfirm --onedir --windowed --hidden-import "loguru" --hidden-import "tkhtmlview" --hidden-import "ttkthemes" --add-data "C:/Users/eahmetshin/Documents/MoldShop_Management_App/MoldShop_app/savings;savings/" --add-data "C:/Users/eahmetshin/Documents/MoldShop_Management_App/MoldShop_app/pics;pics/" --add-data "C:/Users/eahmetshin/Documents/MoldShop_Management_App/MoldShop_app/src;src/" --hidden-import "tkinter.ttk" --hidden-import "tkinter" --hidden-import "pandas" --hidden-import "dotenv" --hidden-import "tkinter.messagebox" --hidden-import "tkinter.filedialog" --hidden-import "idlelib.tooltip" "C:/Users/eahmetshin/Documents/MoldShop_Management_App/MoldShop_app/start.py" --icon "C:/Users/eahmetshin/Documents/MoldShop_Management_App/MoldShop_app/pics/artpack.ico" --name "MoldShop Management"
```