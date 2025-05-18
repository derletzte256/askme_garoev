# Проект: askme_garoev
Базоый клон Stack Overflow на Django

Проект формума вопросов и ответов с базовым функционалом на Django. Выполнен в рамках 1 семестра программы по веб-разработке VK Education в МГТУ им. Н.Э. Баумана. 
Основные аспекты:
- Создание и просмотр вопросов
- Ответы на вопросы
- Лайки вопросов и ответов
- Ранжирование по рейтингу
- Поиск вопросов по названию, содержанию и тегам
- Профиль

## Предварительные требования

* Python 3.8 или выше
* Django 4.2 или выше
* PostgreSQL (для продакшена)
* SQLite (для разработки)

## Установка

1. Клонируйте репозиторий:
   ```sh
   git clone <repository_url>
   cd askme_garoev
   ```

2. Создайте и активируйте виртуальное окружение:
   ```sh
   python -m venv venv
   source venv/bin/activate  # В Windows используйте `venv\Scripts\activate`
   ```

3. Установите необходимые пакеты:
   ```sh
   pip install -r requirements.txt
   ```

4. Настройте базу данных:
   * Для разработки (SQLite):
     ```sh
     python manage.py migrate
     ```
   * Для продакшена (PostgreSQL):
     Настройте параметры базы данных в `askme_garoev/settings.py` и затем выполните:
     ```sh
     python manage.py migrate
     ```

5. Создайте суперпользователя:
   ```sh
   python manage.py createsuperuser
   ```

6. Соберите статические файлы:
   ```sh
   python manage.py collectstatic
   ```

## Запуск проекта

1. Запустите сервер разработки:
   ```sh
   python manage.py runserver
   ```

2. Откройте приложение в веб-браузере по адресу `http://127.0.0.1:8000/`.

## Структура проекта

* `askme_garoev/` - Основная директория проекта
  * `askme_garoev/settings.py` - Настройки проекта
  * `askme_garoev/urls.py` - Конфигурация URL
  * `askme_garoev/wsgi.py` - Конфигурация WSGI
  * `askme_garoev/asgi.py` - Конфигурация ASGI
  * `askme_garoev/manage.py` - Скрипт управления Django
  * `askme_garoev/gunicorn.conf.py` - Конфигурация Gunicorn

* `app/` - Директория приложения
  * `app/models.py` - Модели базы данных
  * `app/views.py` - Представления приложения
  * `app/urls.py` - Конфигурация URL приложения
  * `app/forms.py` - Формы
  * `app/admin.py` - Конфигурация админки
  * `app/tests.py` - Тесты
  * `app/templates/` - HTML шаблоны
  * `app/static/` - Статические файлы (CSS, JS, изображения)
