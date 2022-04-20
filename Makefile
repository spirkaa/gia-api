.POSIX:

export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1

default: build

IMAGE_FULLNAME=git.devmem.ru/cr/gia/api
build:
	@docker build \
		--tag ${IMAGE_FULLNAME} \
		-f .docker/django/ci.Dockerfile .

prod:
	@docker-compose up -d --build
	@docker exec gia-api_django_1 python /app/manage.py migrate
	@docker-compose logs -f

prod-down:
	@docker-compose down

staging:
	@mkdir -p data/staging/{backups,redis,staticfiles}
	@docker-compose -f docker-compose.staging.yml up -d --build
	@docker exec gia-api_django-staging_1 python /app/gia-api/manage.py migrate
	@docker-compose -f docker-compose.local.yml logs -f

staging-down:
	@docker-compose -f docker-compose.staging.yml down

local:
	@docker-compose -f docker-compose.local.yml up -d --build
	@docker exec gia-api_django-local_1 python /app/gia-api/manage.py migrate
	@docker-compose -f docker-compose.local.yml logs -f

local-down:
	@docker-compose -f docker-compose.local.yml down

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
