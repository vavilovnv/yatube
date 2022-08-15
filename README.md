# yatube_project
🌐 Cоциальная сеть позволяющая создавать текстовые посты, при желании дополнять их картинками, комментировать, подписываться на авторов постов и группы постов.

## Описание
💻 Учебный проект по Django 2.2 из курса от Yandex Practicum: python backend-developer. В развернутом виде проект можно посмотреть по адресу [vnv.pythonanywhere.com](vnv.pythonanywhere.com).

## Порядок установки и запуска приложения на localhost
- Установите и активируйте виртуальное окружение
```
# Windows:
source venv/Scripts/activate 

# MacOS или Linux:
source venv/bin/activate 
```
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 
- Перейти в директорию yatube c файлом manage.py:
```
cd .\yatube\
```
- Выполнить миграции:
```
python .\manage.py makemigrations
python .\manage.py migrate
```
- Создать суперпользователя:
```
python .\manage.py createsuperuser
```
- Запуск сервера в dev-режиме:
```
python manage.py runserver
```
- Для запуска приложения открыть его по адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

![Python](https://img.shields.io/badge/-Python_3-blue) ![Django](https://img.shields.io/badge/-Django_2.2-darkgreen) ![Visitor Badge](https://visitor-badge.laobi.icu/badge?page_id=vavilovnv.yatube_project)

