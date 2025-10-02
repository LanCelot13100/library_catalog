from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.middleware.error_handling import ErrorHandlingMiddleware
from src.middleware.logging_middleware import setup_logging_middleware
from src.middleware.metrics import prometheus_middleware, get_metrics
from src.core.logger import setup_logging, get_logger
from src.core.db import create_tables, close_db_connection, check_db_connection
from src.controllers.book_controller import router as book_router

logger = get_logger(__name__)



@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Управляет запуском и остановкой приложения"""

    logger.info("Starting up Library API application")

    try:
        await create_tables()
        logger.info("Database tables created/verified")

        db_healthy = await check_db_connection()
        if db_healthy:
            logger.info("Database connection verified")
        else:
            logger.warning("Database connection failed, but continuing startup")

        logger.info("Application startup completed successfully")

    except Exception as e:
        logger.error(f"Error during application startup: {e}")
        raise

    yield  # приложение работает

    # Shutdown events
    logger.info("Shutting down Library API application")

    try:
        await close_db_connection()
        logger.info("Database connections closed")
        logger.info("Application shutdown completed")

    except Exception as e:
        logger.error(f"Error during application shutdown: {e}")



def create_app() -> FastAPI:
    """Создает и настраивает FastAPI приложение"""

    # Инициализируем систему логирования
    setup_logging()
    logger.info("Creating FastAPI application")

    # Создаем основное приложение
    fastapi_app = FastAPI(
        title="Library Management API",
        description="API для управления библиотекой книг",
        version="1.0.0",
        lifespan=lifespan
    )

    fastapi_app.add_middleware(ErrorHandlingMiddleware)  # обработка ошибок (первым)
    setup_logging_middleware(fastapi_app)  # логирование HTTP запросов
    fastapi_app.middleware("http")(prometheus_middleware)  # метрики Prometheus
    fastapi_app.include_router(book_router)  # подключаем все эндпоинты для работы с книгами
    fastapi_app.add_api_route("/metrics", get_metrics, methods=["GET"])  # эндпоинт для сбора метрик

    logger.info("FastAPI application created and configured")  # логируем завершение конфигурации
    return fastapi_app  # возвращаем настроенное приложение


app = create_app()  # Точка входа всего приложения
