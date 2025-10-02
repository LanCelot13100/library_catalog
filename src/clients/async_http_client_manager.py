"""
Модуль async_http_client_manager.py отвечает за централизованное управление 
асинхронными HTTP-сессиями в проекте с защитой от race conditions и 
правильным управлением ресурсами.
"""
from src.core.logger import get_logger
from typing import Optional
import asyncio
import aiohttp
import os



logger = get_logger(__name__)


class AsyncHttpClientManager: #  Singleton менеджер для управления единой aiohttp сессией.

    _session: Optional[aiohttp.ClientSession] = None
    _lock: asyncio.Lock = asyncio.Lock()
    _session_requests_count: int = 0

    @classmethod
    def _get_connector_config(cls) -> dict: # Получает конфигурацию TCP коннектора из переменных окружения и возвращает словарь с параметрами для TCPConnector
        return {
            'limit': int(os.getenv('HTTP_POOL_LIMIT', '100')),
            'limit_per_host': int(os.getenv('HTTP_POOL_LIMIT_PER_HOST', '30')),
            'ttl_dns_cache': int(os.getenv('HTTP_DNS_CACHE_TTL', '300')),
            'use_dns_cache': True,
        }

    @classmethod
    def _get_timeout_config(cls) -> aiohttp.ClientTimeout: #  Создает и возвращает объект ClientTimeout с настройками таймаутов.
        return aiohttp.ClientTimeout(
            total=int(os.getenv('HTTP_TIMEOUT_TOTAL', '30')),
            connect=int(os.getenv('HTTP_TIMEOUT_CONNECT', '10')),
            sock_read=int(os.getenv('HTTP_TIMEOUT_SOCK_READ', '10')),
        )

    @classmethod
    async def get_session(cls) -> aiohttp.ClientSession: #  Создает и возвращает единую HTTP сессию для всего приложения (Thread-safe метод с double-checked locking паттерном)
        if cls._session is not None and not cls._session.closed:
            cls._session_requests_count += 1
            return cls._session

        # Если сессии нет или она закрыта - входим в критическую секцию
        async with cls._lock:  # Блокируем доступ другим корутинам -> Вторая проверка УЖЕ ПОД БЛОКИРОВКОЙ (double-checked locking)
            if cls._session is not None and not cls._session.closed:
                cls._session_requests_count += 1
                return cls._session

            logger.info("Creating new aiohttp session")

            connector: Optional[aiohttp.TCPConnector] = None
            session: Optional[aiohttp.ClientSession] = None

            try:

                connector = aiohttp.TCPConnector(**cls._get_connector_config())
                timeout = cls._get_timeout_config()
                session = aiohttp.ClientSession(
                    connector=connector,
                    timeout=timeout,
                )


                cls._session = session
                cls._session_requests_count += 1


                logger.info(
                    f"Successfully created aiohttp session. "
                    f"Pool limit: {cls._get_connector_config()['limit']}, "
                    f"Per-host limit: {cls._get_connector_config()['limit_per_host']}"
                )


                return cls._session

            except Exception as e:
                logger.error(f"Failed to create aiohttp session: {e}")

                if session:
                    try:
                        await session.close()
                    except Exception as close_error:
                        logger.error(f"Error closing failed session: {close_error}")

                if connector:
                    try:
                        await connector.close()
                    except Exception as connector_error:
                        logger.error(f"Error closing connector: {connector_error}")

                cls._session = None
                raise

    @classmethod
    async def close(cls) -> None: #  Безопасно закрывает HTTP сессию и освобождает все ресурсы. Должен вызываться при завершении работы приложения.

        if cls._session and not cls._session.closed:
            logger.info(f"Closing aiohttp session. Total requests served: {cls._session_requests_count}")

            try:
                await cls._session.close()
                await asyncio.sleep(0.25)

                logger.info("Successfully closed aiohttp session")

            except Exception as e:
                logger.error(f"Error while closing aiohttp session: {e}")

            finally:
                cls._session = None # В любом случае обнуляем переменную класса, чтобы при следующем обращении создалась новая сессия
                cls._session_requests_count = 0

    @classmethod
    async def __aenter__(cls): #  Позволяет использовать класс с async with (открытие сессии).
        return await cls.get_session()

    @classmethod
    async def __aexit__(cls, exc_type, exc_val, exc_tb):  #  Автоматически закрывает сессию при выходе из контекста.
        """
        Args:
            exc_type: Тип исключения (если было)
            exc_val: Значение исключения (если было) 
            exc_tb: Трассировка исключения (если было)
        """
        await cls.close()

    @classmethod
    def get_stats(cls) -> dict: #  Возвращает статистику использования менеджера сессий.
        return {
            'session_exists': cls._session is not None,
            'session_closed': cls._session.closed if cls._session else True,
            'total_requests_served': cls._session_requests_count,
            'connector_config': cls._get_connector_config(),
        }