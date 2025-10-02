"""Исключения для технической инфраструктуры приложения"""


class ApiClientError(Exception):
    """Ошибка при работе с внешним API"""
    pass


class StorageError(Exception):
    """Ошибка при работе с хранилищем данных"""
    pass


class MetadataClientError(Exception):
    """Ошибка при работе с клиентом метаданных"""
    pass


class AppValidationError(Exception):
    """Ошибка при валидации данных"""
    pass


class BookServiceError(Exception):
    """Ошибка бизнес-логики на уровне сервисов"""
    pass