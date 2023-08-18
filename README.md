# Facetube
## ОПИСАНИЕ:
Facetube - это учебный проект, в рамках изучения Django, разработан по классической МVТ архитектуре. В проекте реализована публикация постов пользователя, подписка, отзывы и комментарии на посты, сохранение постов с фото в базу данных. Проект включает в себя необходимые для работы Веб-сервиса компоненты, такие как маршрутизация URL, шаблоны, модели, представления. Используется пагинация постов и кэширование. Регистрация реализована с верификацией данных, сменой и восстановлением пароля через почту. Написаны тесты, проверяющие работу сервиса.

Благодаря данному проекту блогеры смогут публиковать свои личные дневники, вести блоги и применять социальную коммуникацию. 
## СТЕК ТЕХНОЛОГИЙ:
Python 3.9.10, Django 2.2.16, SQLite3, templates, Pillow, sorl.thumbnail, pytest, django-debug-toolbar

## ЛОКАЛЬНАЯ УСТАНОВКА (для Windows):

1. Клонируй проект на свой компьютер:
```
git clone git@github.com:smaspb17/facetube.git
```
2. Перейди в директорию facetube:
```
cd facetube/
```
3. Создай виртуальное окружение для проекта. Это позволит изолировать проект от системных зависимостей и установленных библиотек. Для создания виртуального окружения используй команду. Требуемая версия python - 3.9.10:
```
python -m venv venv
```
4. Активируй виртуальное окружение командой:
```
source venv/Scripts/activate
```
5. Установи необходимые пакеты и зависимости проекта через менеджер пакетов `pip` и `requirements.txt` файл. Он должен содержать в себе список всех зависимостей, необходимых для работы проекта:
```
pip install -r requirements.txt
```
6. При необходимости обнови пакетный менеджер pip:
``` 
python.exe -m pip install --upgrade pip
```
7. Перейди в директорию surveys, там находится файл manage.py:
```cmd
cd yatube/
```
8. Выполни миграции:
```cmd
python manage.py migrate
```
9. Соберите статистические файлы:
```cmd
python manage.py collectstatic
```
10. Создай суперпользователя:
```cmd
python manage.py createsuperuser
```
11. Запусти проект на локальном сервере:
```
python manage.py runserver
```
12. Перейди по ссылке в браузере на веб-сайт:
```
http://127.0.0.1:8000/
```
13. Запусти тесты через pytest
```cmd
cd ..
```
```cmd
pytest
```
Теперь ты можешь использовать проект на своём компьютере. Если ты хочешь остановить проект, нажми Ctrl+C в терминале, а затем деактивируй виртуальное окружение командой:
```cmd
deactivate
```

## АВТОР:

Шайбаков Марат

## ЛИЦЕНЗИЯ:

нет

## КОНТАКТЫ:

smaspb17@yandex.ru

