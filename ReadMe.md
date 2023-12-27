# [__`MoldShop Management App`__](https://www.artpackplastics.com/)

## __Приложение для управления пресс-формами__
---
Предназначенно для оптимизации работы департамента обслуживания пресс-форм (п/ф).

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

---

## Применяемый стек

- Python - На данном языке написан весь исполняемый код
- Tkinter - Библиотека для реализации графического интерфейса пользователя
- SQLIte3 - Используемая база данных для хранения всей информации
- Pandas и Openpyxl - Библиотеки для взаимодействия с Excel файлами
- HTML - Язык разметки, который применим для некоторых описаний в приложении

## Упаковка приложения в EXE файл

Установить в виртуальное окружение библиотеку pyinstaller

```sh
pip install pyinstaller
```

Запустить в терминале следующий скрипт (необходимо скорректировать некоторые ссылки, чтобы запустились на другом ПК):

```sh
pyinstaller --noconfirm --onedir --windowed --hidden-import "loguru" --hidden-import "tkhtmlview" --hidden-import "ttkthemes" --add-data "D:/MoldShop_poject/savings;savings/" --add-data "D:/MoldShop_poject/pics;pics/" --add-data "D:/MoldShop_poject/src;src/" --hidden-import "tkinter.ttk" --hidden-import "tkinter" --hidden-import "pandas" --hidden-import "dotenv" --hidden-import "tkinter.messagebox" --hidden-import "tkinter.filedialog" --hidden-import "idlelib.tooltip" "D:/MoldShop_poject/start.py" --icon "D:/MoldShop_poject/pics/artpack.ico" --name "MoldShop Management"
```
