import time
import uuid
from fastapi import FastAPI, Request
from src.core.logger import get_logger, set_request_id

logger = get_logger(__name__)

def setup_logging_middleware(app: FastAPI):
    """Настраивает middleware для логирования HTTP запросов"""

    @app.middleware("http")  # регистрируем middleware для всех HTTP запросов
    async def logging_middleware(request: Request, call_next):  # middleware для логирования каждого запроса

        request_id = str(uuid.uuid4())[:8]  # короткий уникальный идентификатор запроса
        set_request_id(request_id)

        # Извлекаем информацию о запросе
        method = request.method
        url = str(request.url)
        user_agent = request.headers.get("user-agent", "Unknown")
        client_ip = request.client.host if request.client else "Unknown"

        # Логируем начало обработки запроса
        logger.info(
            f"Request started: {method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": method,
                "url": url,
                "path": request.url.path,
                "user_agent": user_agent,
                "client_ip": client_ip,
                "query_params": str(request.query_params) if request.query_params else None
            }
        )

        start_time = time.time()  # засекаем время начала обработки

        try:
            response = await call_next(request)
            duration = time.time() - start_time


            logger.info(
                f"Request completed: {method} {request.url.path} -> {response.status_code}",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "response_size": response.headers.get("content-length", "Unknown")
                }
            )


            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            duration = time.time() - start_time

            # Логируем ошибку с полной информацией
            logger.error(
                f"Request failed: {method} {request.url.path} -> ERROR",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "duration_ms": round(duration * 1000, 2),
                },
                exc_info=True
            )

            raise  # перебрасываем исключение для обработки error_handling middleware


def log_response_details(response, request_id: str, duration: float):
    """Логирует дополнительные детали ответа (при необходимости)"""

    # Логируем медленные запросы (больше 1 секунды)
    if duration > 1.0:
        logger.warning(
            f"Slow request detected: {duration:.2f}s",
            extra={
                "request_id": request_id,
                "duration_ms": round(duration * 1000, 2),
                "status_code": response.status_code
            }
        )

    # Логируем ошибки клиента (4xx коды)
    if 400 <= response.status_code < 500:
        logger.warning(
            f"Client error response: {response.status_code}",
            extra={
                "request_id": request_id,
                "status_code": response.status_code
            }
        )