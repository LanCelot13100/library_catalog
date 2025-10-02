from src.core.logger import get_logger
import aiohttp
from src.clients.async_http_client_manager import AsyncHttpClientManager
from typing import Optional, Dict, Any
from abc import ABC
from src.core.exceptions import ApiClientError

logger = get_logger(__name__)



class BaseApiClient(ABC):
    """
    Базовый класс для всех HTTP API клиентов.
    Предоставляет общую функциональность для HTTP запросов.
    """
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip('/')
        self.default_headers = headers or {}

    async def _get_session(self) -> aiohttp.ClientSession:
        """Получает HTTP сессию через менеджер"""
        return await AsyncHttpClientManager.get_session()  # используем общую сессию без модификации

    def _merge_headers(self, request_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Объединяет заголовки по умолчанию с заголовками конкретного запроса"""
        merged = self.default_headers.copy()
        if request_headers:
            merged.update(request_headers)
        return merged

    def _sanitize_log_data(self, data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Удаляет конфиденциальные данные из логов"""
        if not data:
            return {}

        sensitive_keys = {'password', 'token', 'key', 'secret', 'authorization','api_key'}  # список конфиденциальных ключей
        sanitized = {}

        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in
                   sensitive_keys):
                sanitized[key] = "***REDACTED***"
            else:
                sanitized[key] = value
        return sanitized  # возвращаем очищенные данные

    async def _make_request(  # универсальный метод для выполнения HTTP запросов
            self,
            method: str,
            endpoint: str,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[float] = None,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Выполняет HTTP запрос к API

        Args:
            method: HTTP метод
            endpoint: Путь к эндпоинту (начинающийся с /)
            headers: Дополнительные заголовки
            timeout: Таймаут запроса
            **kwargs: Параметры запроса (params, json, data)

        Returns:
            Dict: JSON ответ от сервера

        Raises:
            ApiClientError: При ошибках HTTP запроса
        """
        url = f"{self.base_url}{endpoint}"
        session = await self._get_session()
        merged_headers = self._merge_headers(headers)

        request_kwargs = kwargs.copy()
        request_kwargs['headers'] = merged_headers

        if timeout:
            request_kwargs['timeout'] = aiohttp.ClientTimeout(total=timeout)

        sanitized_params = self._sanitize_log_data(kwargs.get('params'))
        sanitized_json = self._sanitize_log_data(kwargs.get('json'))
        logger.info(f"{method.upper()} {url} | params={sanitized_params} json={sanitized_json}")

        try:
            async with session.request(method, url, **request_kwargs) as response:
                response.raise_for_status()

                content_type = response.headers.get('content-type', '').lower()
                if 'application/json' in content_type:
                    return await response.json()
                else:
                    text_content = await response.text()
                    logger.warning(f"Non-JSON response from {url}: {content_type}")
                    return {'text': text_content}

        except aiohttp.ClientError as e:
            logger.error(f"HTTP client error for {method.upper()} {url}: {e}")
            raise ApiClientError(f"HTTP request failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error for {method.upper()} {url}: {e}")
            raise ApiClientError(f"Unexpected error during HTTP request: {e}")

    # Удобные методы для популярных HTTP операций
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Выполняет GET запрос"""
        return await self._make_request('GET', endpoint, params=params, **kwargs)

    async def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Выполняет POST запрос"""
        return await self._make_request('POST', endpoint, json=json, **kwargs)

    async def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """Выполняет PUT запрос"""
        return await self._make_request('PUT', endpoint, json=json, **kwargs)

    async def delete(self, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Выполняет DELETE запрос"""
        return await self._make_request('DELETE', endpoint, **kwargs)

