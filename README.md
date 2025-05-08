# GIA API

UI и парсер таблиц Excel с сайта РЦОИ г. Москвы со списками работников пунктов проведения экзаменов (ППЭ) ГИА, ОГЭ, ЕГЭ.

## Разработка

Разработка нового функционала ведётся в ветках, по готовности делается PR в `main`. Минимальные изменения и багфиксы сразу вносятся в `main`.

```shell
uv sync --dev --group=test
pre-commit install
```

### CI/CD (Jenkinsfile по-русски)

В пайплайне определены этапы `Build`, `Build and push`, `Test`, `Deploy`, которые запускаются в соответствии с условиями в блоках `when`.

1. PR или коммит в любую ветку, кроме `main`, запускает `Build` и `Test`.
1. Коммит в `main` запускает `Build and push` и `Test`.
1. `Deploy` запускается вручную в разделе `Build with Parameters`, при этом можно принудительно выполнить `Build and push`, а `Test` будет пропущен.
1. Автоматический деплой на тестовое или стейджинг окружение не предусмотрен.

### Запуск local (разработка)

1. Переименовать файл `env.local-example` в `.env.local`
1. Настроить переменные в файле `.env.local`
1. Последовательно выполнить команды

```shell
make local
make local-runjobs
make local-test
```

1. <http://localhost:8000/>

### Запуск staging (= prod + local)

1. Переименовать файл `env.staging-example` в `.env.staging`
1. Настроить переменные в файле `.env.staging`
1. Последовательно выполнить команды

```shell
make staging
make staging-runjobs
make staging-test
```

1. <http://localhost:8080/>
