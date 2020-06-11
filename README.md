# GIA API

Данные с сайта РЦОИ города Москвы о распределении сотрудников образовательных организаций в ППЭ.

## Запуск local (разработка)

1. Переименовать файл `env.local-example` в `.env.local`
1. Настроить переменные в файле `.env.local`
1. Последовательно выполнить команды

        docker-compose -f docker-compose.local.yml up -d --build
        docker exec -it gia-api_django-local_1 python manage.py migrate
        docker exec -it gia-api_django-local_1 python manage.py createsuperuser

1. Открыть админку Django <http://localhost:8000/admin>

    * Добавить в разделе RCOI -> Data sources ссылки на страницы сайта РЦОИ с расписанием
    * Нажать кнопку Обновить БД


## Запуск prod

1. Переименовать файл `env.example` в `.env`
1. Настроить переменные в файле `.env`
1. Последовательно выполнить команды

        docker-compose up -d --build
        docker exec -it gia-api_django_1 python manage.py migrate
        docker exec -it gia-api_django_1 python manage.py createsuperuser

1. Открыть админку Django <http://example.com/admcenter>

    * Добавить в разделе RCOI -> Data sources ссылки на страницы сайта РЦОИ с расписанием
    * Нажать кнопку Обновить БД

## Запуск staging (= prod + local)

1. Переименовать файл `env.staging-example` в `.env.staging`
1. Настроить переменные в файле `.env.staging`
1. Последовательно выполнить команды

        docker-compose -f docker-compose.staging.yml up -d --build
        docker exec -it gia-api_django-staging_1 python manage.py migrate
        docker exec -it gia-api_django-staging_1 python manage.py createsuperuser

1. Открыть админку Django <http://localhost:8080/admcenter>

    * Добавить в разделе RCOI -> Data sources ссылки на страницы сайта РЦОИ с расписанием
    * Нажать кнопку Обновить БД


## Ручное обновление БД (не забудь поменять имя контейнера)

    docker exec -it gia-api_django_1 python manage.py shell_plus
    from apps.rcoi.models import RcoiUpdater
    RcoiUpdater().run()
    exit()
    docker-compose restart
