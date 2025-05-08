.POSIX:

export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
export BUILDKIT_PROGRESS=plain

help: ## Show this help
	@echo "Usage: make [target]"
	@echo "Targets:"
	@awk '/^[a-zA-Z0-9_-]+:.*?##/ { \
		helpMessage = match($$0, /## (.*)/); \
		if (helpMessage) { \
			target = $$1; \
			sub(/:/, "", target); \
			printf "  \033[36m%-20s\033[0m %s\n", target, substr($$0, RSTART + 3, RLENGTH); \
		} \
	}' $(MAKEFILE_LIST)

all: help

staging:
	@mkdir -p data/staging/staticfiles
	@docker compose -f docker-compose.staging.yml up -d --build
	@docker exec gia-api-django-staging-1 python /app/gia-api/manage.py migrate
	@docker compose -f docker-compose.staging.yml logs -f

staging-runjobs:
	@docker exec gia-api-django-staging-1 python /app/gia-api/manage.py loaddata datasource
	@docker exec gia-api-django-staging-1 python /app/gia-api/manage.py runjobs hourly
	@docker exec gia-api-django-staging-1 python /app/gia-api/manage.py invalidate all

staging-test:
	@docker compose -f docker-compose.staging.yml up -d --build
	@docker exec gia-api-django-staging-1 pytest

staging-down:
	@docker compose -f docker-compose.staging.yml down

local:  ## Run app in docker
	@docker compose -f docker-compose.local.yml up -d --build
	@docker exec gia-api-django-local-1 python /app/gia-api/manage.py migrate
	@docker compose -f docker-compose.local.yml logs -f

local-runjobs:  ## Run jobs
	@docker exec gia-api-django-local-1 python /app/gia-api/manage.py loaddata datasource
	@docker exec gia-api-django-local-1 python /app/gia-api/manage.py runjobs hourly

local-test:  ## Run tests in docker. Additional args can be passed to pytest (e.g. args="-k test_something")
	@docker compose -f docker-compose.local.yml up -d --build
	@docker exec -it -e "DJANGO_DEBUG_TOOLBAR=False" gia-api-django-local-1 pytest -vv --cov-report html $(args)

local-down:  ## Stop app in docker
	@docker compose -f docker-compose.local.yml down

local-migrations:  ## Generate migrations
	@docker exec -it gia-api-django-local-1 python /app/gia-api/manage.py makemigrations

local-migrate:  ## Apply migrations
	@docker exec -it gia-api-django-local-1 python /app/gia-api/manage.py migrate

local-admin:  ## Create superuser
	@docker exec -it gia-api-django-local-1 sh -c '\
	DJANGO_SUPERUSER_USERNAME=admin \
	DJANGO_SUPERUSER_PASSWORD=admin \
	DJANGO_SUPERUSER_EMAIL="admin@admin.com" \
	python /app/gia-api/manage.py createsuperuser --noinput'

local-exec:  ## Run bash in docker
	@docker exec -it gia-api-django-local-1 bash

local-shell:  ## Run django shell with autoloading of the apps database models and subclasses of user-defined classes
	@docker exec -it gia-api-django-local-1 python /app/gia-api/manage.py shell_plus

local-dropdb: local-down  ## Stop containers and delete database volume
	@docker volume rm $$(docker volume ls | grep -E "gia-api_postgres_data_local$$" | awk '{print $$2}')

down: ## Stop app in docker
	@make prod-down --no-print-directory --ignore-errors
	@make staging-down --no-print-directory --ignore-errors
	@make local-down --no-print-directory --ignore-errors

cleanup-images:  ## Cleanup images
	@docker rmi -f \
		gia-api-django-local \
		gia-api-postgres-local \
		gia-api-django-staging \
		gia-api-postgres-staging \
		gia-api-redis-staging \
		gia-api-nginx-staging \
		gia-api-django \
		gia-api-postgres \
		gia-api-redis \
		gia-api-nginx
