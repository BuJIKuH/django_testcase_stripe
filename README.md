Проект под тестовое задание.

Для запуска приложения:
1. Скачиваем с репозитория проект на локальную машину.
2. Создаем виртуальное окружение.
3. Устанавливаем зависимости командой pip freeze -r requirements.txt
4. Если есть желание добавить свои товары, то выполняем следующие действия:
   1. Создаем миграции командой python manage.py makemigrations 
   2. Устанавливаем миграции python manage.py migrate
   3. Создаем супер пользователя python manage.py createsuperuser
5. Запускаем проект командой python manage.py runserver и переходим по 
   адресу  http://127.0.0.1:8000/
