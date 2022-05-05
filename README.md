# GIA API

Парсер таблиц Excel с сайта РЦОИ города Москвы со списками сотрудников пунктов проведения экзаменов (ППЭ).

## Разработка

Ведётся в ветках, по готовности делается PR в мастер.
Минимальные изменения и багфиксы могут вноситься сразу в мастер.

### CI/CD (расшифровка .drone.yml)

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

### Запуск local (разработка)

1. Переименовать файл `env.local-example` в `.env.local`
1. Настроить переменные в файле `.env.local`
1. Последовательно выполнить команды

        docker-compose -f docker-compose.local.yml up -d --build
        docker exec gia-api_django-local_1 python /app/gia-api/manage.py migrate
        docker exec gia-api_django-local_1 python /app/gia-api/manage.py loaddata datasource
        docker exec -it gia-api_django-local_1 python /app/gia-api/manage.py createsuperuser
        docker exec gia-api_django-local_1 python /app/gia-api/manage.py runjobs hourly

1. <http://localhost:8000/>

### Запуск staging (= prod + local)

1. Переименовать файл `env.staging-example` в `.env.staging`
1. Настроить переменные в файле `.env.staging`
1. Последовательно выполнить команды

        docker-compose -f docker-compose.staging.yml up -d --build
        docker exec gia-api_django-staging_1 python /app/gia-api/manage.py migrate
        docker exec gia-api_django-staging_1 python /app/gia-api/manage.py loaddata datasource
        docker exec gia-api_django-staging_1 python /app/gia-api/manage.py invalidate all
        docker exec -it gia-api_django-staging_1 python /app/gia-api/manage.py createsuperuser
        docker exec gia-api_django-staging_1 python /app/gia-api/manage.py runjobs hourly

1. <http://localhost:8080/>

### Запуск prod

1. Переименовать файл `env.example` в `.env`
1. Настроить переменные в файле `.env`
1. Последовательно выполнить команды

        docker-compose up -d --build
        docker exec gia-api_django_1 python /app/manage.py migrate
        docker exec gia-api_django_1 python /app/manage.py loaddata datasource
        docker exec -it gia-api_django_1 python /app/manage.py createsuperuser
        docker exec gia-api_django_1 python /app/manage.py runjobs hourly

1. <http://example.com/>

## Ручное обновление БД (не забудь поменять имя контейнера)

    docker exec -it gia-api_django_1 python /app/manage.py shell_plus
    from apps.rcoi.models import RcoiUpdater
    RcoiUpdater().run()
    exit()
    docker-compose restart

## Новый сезон

1. Очистить таблицы и начать автоинкремент id с начала

        docker exec -it gia-db psql -U gia
        TRUNCATE rcoi_datafile, rcoi_date, rcoi_employee, rcoi_exam, rcoi_level, rcoi_organisation, rcoi_place, rcoi_position, rcoi_subscription RESTART IDENTITY;
        exit;

1. Вручную отправить письмо подписчикам, чтобы подписались заново

## Обновление версии PostgreSQL

1. Обновить версию в Dockerfile
1. Сделать снапшот ВМ
1. Подключиться к ВМ и выполнить

        docker exec gia-db backup
        docker stop gia-db
        docker run --rm -v /docker/gia-api/db/data:/var/lib/postgresql/12/data -v /docker/gia-api/db/14/data:/var/lib/postgresql/14/data tianon/postgres-upgrade:12-to-14
        docker rmi tianon/postgres-upgrade:12-to-14
        mv /docker/gia-api/db/data /docker/gia-api/db/data_12
        mv /docker/gia-api/db/14/data /docker/gia-api/db/data
        rm -rf /docker/gia-api/db/14
        echo "host all all 0.0.0.0/0 trust" >> /docker/gia-api/db/data/pg_hba.conf

1. Запустить новый контейнер БД
