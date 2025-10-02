"""Конфигурация логирования с поддержкой структурированных логов и request_id"""

import logging
import structlog
from contextvars import ContextVar
import os
from dotenv import load_dotenv

load_dotenv()

request_id_var: ContextVar[str] = ContextVar("request_id", default="") # Контекстная переменная для хранения request_id в рамках одного запроса


def setup_logging():
    """Настраивает логирование для всего приложения"""

    is_dev = os.getenv("ENV", "dev") == "dev"
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(message)s",
        force=True
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.set_exc_info,
            structlog.dev.ConsoleRenderer() if is_dev else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(  # настройка фильтрации логов
            getattr(logging, log_level, logging.INFO)
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Устанавливаем уровень логирования для uvicorn (FastAPI сервер)
    logging.getLogger("uvicorn").setLevel(getattr(logging, log_level, logging.INFO))
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Получает настроенный структурированный логгер

    Args:
        name: Имя логгера (обычно __name__ модуля)

    Returns:
        structlog.BoundLogger: Настроенный логгер
    """
    return structlog.get_logger(name or __name__)


def set_request_id(request_id: str) -> None:
    """Устанавливает request_id в контекст текущего запроса"""
    request_id_var.set(request_id)


def get_request_id() -> str:
    """Получает request_id из контекста текущего запроса"""
    return request_id_var.get()


setup_logging()  # вызываем настройку сразу при импорте