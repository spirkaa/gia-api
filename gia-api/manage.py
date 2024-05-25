#!/usr/bin/env python
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

    from django.conf import settings

    if settings.DEBUG:
        import logging

        logging.getLogger("watchdog.observers.inotify_buffer").setLevel(logging.INFO)

    if (
        settings.OTEL_TRACING_ENABLED
        and os.environ["DJANGO_SETTINGS_MODULE"] == "config.settings.local"
    ):
        from opentelemetry import trace
        from opentelemetry.instrumentation.django import DjangoInstrumentor
        from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor
        from opentelemetry.instrumentation.redis import RedisInstrumentor
        from opentelemetry.sdk.resources import (
            DEPLOYMENT_ENVIRONMENT,
            SERVICE_NAME,
            Resource,
        )
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import (
            ConsoleSpanExporter,
            SimpleSpanProcessor,
        )

        resource = Resource.create(
            attributes={
                SERVICE_NAME: settings.OTEL_SERVICE_NAME,
                DEPLOYMENT_ENVIRONMENT: settings.OTEL_DEPLOYMENT_ENVIRONMENT,
            }
        )

        tracer_provider = TracerProvider(resource=resource)
        tracer_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
        trace.set_tracer_provider(tracer_provider)
        DjangoInstrumentor().instrument()
        PsycopgInstrumentor().instrument()
        RedisInstrumentor().instrument()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
