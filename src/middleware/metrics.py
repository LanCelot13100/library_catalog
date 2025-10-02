from fastapi import Request, Response
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
import time
from src.core.logger import get_logger

logger = get_logger(__name__)

# Метрики Prometheus
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Duration of HTTP requests in seconds",
    ["method", "endpoint"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

REQUEST_IN_PROGRESS = Gauge(
    "http_requests_in_progress",
    "Number of HTTP requests currently being processed",
    ["method", "endpoint"]
)


async def prometheus_middleware(request: Request, call_next):
    """Middleware для автоматического сбора метрик всех HTTP запросов"""

    # Не собираем метрики для самого /metrics эндпоинта (избегаем рекурсии)
    if request.url.path == "/metrics":
        return await call_next(request)

    method = request.method
    endpoint = request.url.path

    # Увеличиваем счетчик активных запросов
    REQUEST_IN_PROGRESS.labels(method=method, endpoint=endpoint).inc()

    start_time = time.time()  # засекаем время начала обработки

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # Записываем метрики успешного запроса
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(response.status_code)
        ).inc()

        REQUEST_LATENCY.labels(
            method=method,
            endpoint=endpoint
        ).observe(process_time)

        # Логируем медленные запросы для мониторинга
        if process_time > 1.0:
            logger.warning(
                f"Slow request: {method} {endpoint} took {process_time:.2f}s")

        return response

    except Exception as e:
        process_time = time.time() - start_time

        # Записываем метрики неуспешного запроса
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code="500"
        ).inc()

        REQUEST_LATENCY.labels(
            method=method,
            endpoint=endpoint
        ).observe(process_time)

        logger.error(f"Request failed in metrics middleware: {method} {endpoint} - {e}")
        raise

    finally:
        # Уменьшаем счетчик активных запросов в любом случае
        REQUEST_IN_PROGRESS.labels(method=method, endpoint=endpoint).dec()


async def get_metrics() -> Response:
    """
    Эндпоинт для предоставления метрик в формате Prometheus
    Используется Prometheus сервером для сбора метрик
    """
    try:
        metrics_output = generate_latest()
        logger.info("Metrics requested and generated successfully")
        return Response(
            content=metrics_output,
            media_type=CONTENT_TYPE_LATEST
        )
    except Exception as e:
        logger.error(f"Error generating metrics: {e}")
        return Response(
            content="Error generating metrics",
            status_code=500
        )