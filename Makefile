.POSIX:

export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

default: build

IMAGE_FULLNAME=git.devmem.ru/projects/gia-api
build:
	@docker build \
		--tag ${IMAGE_FULLNAME} \
		-f .docker/django/ci.Dockerfile .

prod:
	@docker-compose up -d --build
	@docker-compose logs -f

prod-runjobs:
	@docker exec gia-api_django_1 python /app/manage.py loaddata datasource
	@docker exec gia-api_django_1 python /app/manage.py runjobs hourly

prod-down:
	@docker-compose down

staging:
	@mkdir -p data/staging/{backups,redis,staticfiles}
	@docker-compose -f docker-compose.staging.yml up -d --build
	@docker exec gia-api_django-staging_1 python /app/gia-api/manage.py migrate
	@docker-compose -f docker-compose.staging.yml logs -f

staging-runjobs:
	@docker exec gia-api_django-staging_1 python /app/gia-api/manage.py loaddata datasource
	@docker exec gia-api_django-staging_1 python /app/gia-api/manage.py runjobs hourly
	@docker exec gia-api_django-staging_1 python /app/gia-api/manage.py invalidate all

staging-test:
	@docker-compose -f docker-compose.staging.yml up -d
	@docker exec gia-api_django-staging_1 pytest

staging-down:
	@docker-compose -f docker-compose.staging.yml down

local:
	@docker-compose -f docker-compose.local.yml up -d --build
	@docker exec gia-api_django-local_1 python /app/gia-api/manage.py migrate
	@docker-compose -f docker-compose.local.yml logs -f

local-runjobs:
	@docker exec gia-api_django-local_1 python /app/gia-api/manage.py loaddata datasource
	@docker exec gia-api_django-local_1 python /app/gia-api/manage.py runjobs hourly

local-test:
	@docker-compose -f docker-compose.local.yml up -d
	@docker exec -e "DJANGO_DEBUG_TOOLBAR=False" gia-api_django-local_1 pytest --cov-report html

local-down:
	@docker-compose -f docker-compose.local.yml down

local-migrations:
	@docker exec -it gia-api_django-local_1 python /app/gia-api/manage.py makemigrations

local-migrate:
	@docker exec -it gia-api_django-local_1 python /app/gia-api/manage.py migrate

local-admin:
	@docker exec -it gia-api_django-local_1 sh -c '\
	DJANGO_SUPERUSER_USERNAME=admin \
	DJANGO_SUPERUSER_PASSWORD=admin \
	DJANGO_SUPERUSER_EMAIL="admin@admin.com" \
	python /app/gia-api/manage.py createsuperuser --noinput'

local-exec:
	@docker exec -it gia-api_django-local_1 bash

local-shell:
	@docker exec -it gia-api_django-local_1 python /app/gia-api/manage.py shell_plus

local-dropdb: local-down
	@docker volume rm $$(docker volume ls | grep -E "gia-api_postgres_data_local$$" | awk '{print $$2}')

down:
	@make prod-down --no-print-directory --ignore-errors
	@make staging-down --no-print-directory --ignore-errors
	@make local-down --no-print-directory --ignore-errors

cleanup-images:
	@docker rmi -f \
		gia-api_django-local \
		gia-api_postgres-local \
		gia-api_django-staging \
		gia-api_postgres-staging \
		gia-api_redis-staging \
		gia-api_nginx-staging \
		gia-api_django \
		gia-api_postgres \
		gia-api_redis \
		gia-api_nginx
