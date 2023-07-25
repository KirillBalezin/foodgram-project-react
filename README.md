# praktikum_new_diplom

<h1 align="center"><img src="https://samors.ru/wp-content/uploads/2020/01/PP-obed-3-800x445.jpg" height="200" width="400"/></h1>

## Описание

Приложение «Продуктовый помощник»: сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволяет пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд и скачивать в формате txt. 

В рамках учебного проекта был разработан backend сервиса и настроен CI/CD.

## Доступ

Проект запущен на сервере и доступен по адресу:
- https://kbfoodgram.ddns.net/

Чтобы попасть в панель администратора, необходимо перейти по адресу:
- https://kbfoodgram.ddns.net/admin/
```
почта: admin@mail.ru
пароль: admin
```

## Стек технологий

- Python
- Django
- Django REST Framework
- PostgreSQL
- Docker
- Github Actions

## Зависимости

- Перечислены в файле backend/requirements.txt

## Для запуска проекта на собственном сервере:

1. На сервере создайте директорию foodgram.
2. В директории foodgram необходимо создать файл .env и директорию infra.
3. Файл .env должен быть заполнен следующими данными:
```
SECRET_KEY=<КЛЮЧ>
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<ИМЯ БД>
POSTGRES_USER=<ИМЯ ЮЗЕРА БД>
POSTGRES_PASSWORD=<ПАРОЛЬ БД>
DB_HOST=db
DB_PORT=5432
```
4. В директорию infra необходимо скопировать 2 файла из репозитория:
    - docker-compose.yml
    - nginx.conf
5. Все дальнейшие команды необходимо выполнять из директории infra:
```
sudo docker compose -f docker-compose.yml up -d
sudo docker compose -f docker-compose.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic
```
6. Проект запущен и готов к работе (Ингредиенты и теги создаются в панели администратора).

Для создания суперпользователя, выполните команду:
```
sudo docker compose -f docker-compose.yml exec backend python manage.py createsuperuser
```
Для добавления ингредиентов в бд, выполните команду:
```
sudo docker compose -f docker-compose.yml exec backend python manage.py import_db
```
### Исполнитель
Балезин Кирилл