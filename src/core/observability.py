from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from prometheus_client import make_asgi_app

def setup_observability():
    resource = Resource(attributes={
        ResourceAttributes.SERVICE_NAME: "rag_service"
    })
    
    reader = PrometheusMetricReader()
    provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(provider)

    meter = metrics.get_meter("rag.system.custom_metrics")

    token_counter = meter.create_counter(
        "llm_token_usage_total",
        description="Total tokens consumed by the LLM",
    )

    cache_counter = meter.create_counter(
        "rag_cache_hits_total",
        description="Total cache hits and misses",
    )
    
    api_request_counter = meter.create_counter(
        "api_requests_total",
        description="Total API requests",
    )
    
    api_duration_histogram = meter.create_histogram(
        "api_request_duration_seconds",
        description="API request duration in seconds",
    )

    return token_counter, cache_counter, api_request_counter, api_duration_histogram

token_counter, cache_counter, api_request_counter, api_duration_histogram = setup_observability()
prometheus_app = make_asgi_app()
