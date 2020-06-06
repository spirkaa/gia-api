# GIA API

Данные с сайта РЦОИ города Москвы о распределении сотрудников образовательных организаций в ППЭ.

## Запуск prod

1. Переименовать файл `env.example` в `.env`
1. Настроить переменные в файле `.env`
1. Последовательно выполнить команды

        docker-compose up -d --build
        docker exec -it gia-api_django_1 python manage.py migrate
        docker exec -it gia-api_django_1 python manage.py createsuperuser

1. Открыть админку Django и добавить в DataSource ссылки на страницы сайта РЦОИ с расписанием
1. Последовательно выполнить команды

        docker exec -it gia-api_django_1 python manage.py shell_plus
        from apps.rcoi.models import RcoiUpdater
        RcoiUpdater().run()
        exit()
        docker-compose restart

## Запуск staging (= prod + local)

1. Переименовать файл `env.staging-example` в `.env.staging`
1. Настроить переменные в файле `.env.staging`
1. Последовательно выполнить команды

        docker-compose -f docker-compose.staging.yml up -d --build
        docker exec -it gia-api_django-staging_1 python manage.py migrate
        docker exec -it gia-api_django-staging_1 python manage.py createsuperuser

1. Открыть админку Django и добавить в DataSource ссылки на страницы сайта РЦОИ с расписанием
1. Последовательно выполнить команды

        docker exec -it gia-api_django-staging_1 python manage.py shell_plus
        from apps.rcoi.models import RcoiUpdater
        RcoiUpdater().run()
        exit()
        docker-compose restart
