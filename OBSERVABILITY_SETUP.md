# Learning Platform Observability Setup

This document explains how to set up the complete observability stack for the Learning Platform API.

## What You Get

- **Grafana**: Dashboards and visualization (http://localhost:3000)
- **Prometheus**: Metrics collection and alerting (http://localhost:9090)
- **Loki**: Log aggregation (http://localhost:3100)
- **Tempo**: Distributed tracing (http://localhost:3200)
- **Promtail**: Log shipper to Loki
- **Node Exporter**: System metrics (http://localhost:9100)
- **cAdvisor**: Container metrics (http://localhost:8080)

## Quick Start

1. **Start the observability stack:**
   ```bash
   docker-compose -f docker-compose.observability.yml up -d
   ```

2. **Access Grafana:**
   - URL: http://localhost:3000
   - Username: `admin`
   - Password: `admin`

3. **View the Learning Platform dashboard:**
   - Navigate to "Dashboards" → "Learning Platform" folder
   - Open "Learning Platform - Overview"

## Django Integration Required

To get metrics and traces from your Django app, you need to add these packages:

```bash
pip install django-prometheus
pip install opentelemetry-distro[otlp]
pip install opentelemetry-instrumentation-django
pip install opentelemetry-instrumentation-psycopg2
pip install opentelemetry-instrumentation-requests
```

### Add to Django settings.py:

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    'django_prometheus',
    # ... your other apps
]

# Add to MIDDLEWARE (at the beginning and end)
MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',
    # ... your existing middleware
    'django_prometheus.middleware.PrometheusAfterMiddleware',
]

# Add metrics endpoint to urls.py
from django.urls import path, include

urlpatterns = [
    path('', include('django_prometheus.urls')),
    # ... your other urls
]
```

### OpenTelemetry Tracing Setup:

```python
# Add this to your settings.py or create a separate tracing.py file
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Initialize tracing
trace.set_tracer_provider(TracerProvider())

# Configure OTLP exporter for Tempo
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",
    insecure=True
)

span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Auto-instrument Django, PostgreSQL, and HTTP requests
DjangoInstrumentor().instrument()
Psycopg2Instrumentor().instrument()
RequestsInstrumentor().instrument()
```

## Custom Metrics Example

Create a `metrics.py` file in your Django app:

```python
from prometheus_client import Counter, Histogram, Gauge

# Business metrics for Learning Platform
student_assessments = Counter(
    'student_assessments_total',
    'Total student assessments',
    ['cohort', 'assessment_type', 'status']
)

github_sync_duration = Histogram(
    'github_sync_duration_seconds',
    'Time spent syncing with GitHub API',
    ['operation']
)

active_students = Gauge(
    'active_students_count',
    'Number of active students',
    ['cohort']
)

# Usage in your views:
from .metrics import student_assessments

def submit_assessment(request):
    # ... your logic
    student_assessments.labels(
        cohort=student.cohort.name,
        assessment_type='capstone',
        status='submitted'
    ).inc()
```

## Enhanced Logging

Add request context to your existing structlog setup:

```python
# middleware/logging_middleware.py
import structlog
import uuid

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            user_id=getattr(request.user, 'id', None),
            path=request.path,
            method=request.method,
        )
        
        response = self.get_response(request)
        return response
```

Add to `MIDDLEWARE` in settings.py:
```python
MIDDLEWARE = [
    'your_app.middleware.logging_middleware.RequestLoggingMiddleware',
    # ... other middleware
]
```

## Troubleshooting

### Logs Not Appearing in Loki
- Check that your Django app is writing to `./logs/learning_platform.json`
- Verify Promtail can read the log file (permissions)
- Check Promtail logs: `docker-compose -f docker-compose.observability.yml logs promtail`

### No Django Metrics in Prometheus
- Ensure django-prometheus is installed and configured
- Check that `/metrics` endpoint returns data: `curl http://localhost:8000/metrics`
- Verify Prometheus config points to correct Django host

### Traces Not Showing in Tempo
- Confirm OpenTelemetry is properly configured
- Check Tempo logs: `docker-compose -f docker-compose.observability.yml logs tempo`
- Verify traces are being sent: look for OTLP exports in Django logs

## Managing the Stack

```bash
# Start all services
docker-compose -f docker-compose.observability.yml up -d

# Stop all services
docker-compose -f docker-compose.observability.yml down

# View logs
docker-compose -f docker-compose.observability.yml logs -f [service-name]

# Remove all data (destructive!)
docker-compose -f docker-compose.observability.yml down -v
```

## Next Steps

1. Set up alerting rules in Prometheus
2. Create custom dashboards for your specific business metrics
3. Configure log retention policies
4. Set up backup for Grafana dashboards
5. Add PostgreSQL monitoring with postgres_exporter