"""Исключения бизнес-логики домена"""


class BookAlreadyExistsError(Exception):
    """Книга с таким названием и автором уже существует"""
    pass


class InvalidBookDataError(Exception):
    """Некорректные данные книги"""
    pass


class NotificationError(Exception):
    """Ошибка при отправке уведомлений"""
    pass


class BookNotFoundError(Exception):
    """Книга не найдена"""
    pass