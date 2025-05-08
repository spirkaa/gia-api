from uuid import uuid4

from django.conf import settings

if settings.OTEL_TRACING_ENABLED and settings.OTEL_EXPORTER_OTLP_ENDPOINT:
    from opentelemetry import metrics, trace
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
        OTLPMetricExporter,
    )
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
        OTLPSpanExporter,
    )
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import (
        DEPLOYMENT_ENVIRONMENT,
        SERVICE_INSTANCE_ID,
        SERVICE_NAME,
        Resource,
    )
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    def post_fork(_, worker):
        """Configure opentelemetry after forking worker processes."""
        resource = Resource.create(
            attributes={
                SERVICE_NAME: settings.OTEL_SERVICE_NAME,
                DEPLOYMENT_ENVIRONMENT: settings.OTEL_DEPLOYMENT_ENVIRONMENT,
                SERVICE_INSTANCE_ID: str(uuid4()),
                "worker": worker.pid,
            },
        )

        tracer_provider = TracerProvider(resource=resource)
        tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
        trace.set_tracer_provider(tracer_provider)

        metrics.set_meter_provider(
            MeterProvider(
                resource=resource,
                metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter())],
            ),
        )
