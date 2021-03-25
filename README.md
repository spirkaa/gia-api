# GIA API

[![Build Status](https://drone.devmem.ru/api/badges/piv/gia-api/status.svg)](https://drone.devmem.ru/piv/gia-api)

Разработка ведётся в ветках, по готовности делается PR в мастер.
Минимальные изменения и багфиксы могут вноситься сразу в мастер.


## CI/CD (расшифровка .drone.yml)

В файле определены 3 пайплайна - `test`, `build`, `deploy`.
Каждый пайплайн запускается в соответствии определенными для него триггерами.

1. Любой коммит запускает `test`.
1. Коммит в мастер запускает `test`, потом `build`.
1. Ввиду отсутствия необходимости в данном проекте
   тестового или стейджинг окружений, автоматического деплоя нет.
1. `deploy` запускается вручную командой `drone build promote piv/gia-api 54 prod`

    * `piv/gia-api` - репозиторий
    * `54` - номер билда в Drone
    * `prod` - название окружения, указанное в `when: target:`
    * Тэг образа для Ansible передается в переменной окружения `image_tag`
    * В плейбуке не задан тэг по-умолчанию,
      то есть `latest` никак не окажется развернутым через пайплайн


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

## Новый сезон

### Очистить таблицы и начать автоинкремент id с начала.

    docker exec -it gia-db psql -U gia
    TRUNCATE rcoi_datafile, rcoi_date, rcoi_employee, rcoi_exam, rcoi_level, rcoi_organisation, rcoi_place, rcoi_position, rcoi_subscription RESTART IDENTITY;
    exit;

### Вручную отправить письмо подписчикам, чтобы подписались заново.
