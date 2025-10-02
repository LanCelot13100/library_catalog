from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.exceptions import ApiClientError, StorageError, MetadataClientError, BookServiceError
from src.domain.exceptions import BookAlreadyExistsError, InvalidBookDataError, BookNotFoundError
from src.core.logger import get_logger, get_request_id
import traceback

logger = get_logger(__name__)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware для централизованной обработки ошибок и возврата унифицированных ответов"""

    async def dispatch(self, request: Request, call_next):  # основной метод обработки запросов
        try:
            response = await call_next(request)
            return response

        # Обработка доменных исключений (бизнес-логика)
        except BookAlreadyExistsError as e:
            logger.warning(f"Book already exists: {e}", extra={"request_path": str(request.url.path)})
            return self._create_error_response(
                status_code=409,  # Conflict
                error_code="BOOK_ALREADY_EXISTS",
                message=str(e),
                request=request
            )

        except BookNotFoundError as e:
            logger.warning(f"Book not found: {e}", extra={"request_path": str(request.url.path)})
            return self._create_error_response(
                status_code=404,  # Not Found
                error_code="BOOK_NOT_FOUND",
                message=str(e),
                request=request
            )

        except InvalidBookDataError as e:
            logger.warning(f"Invalid book data: {e}", extra={"request_path": str(request.url.path)})
            return self._create_error_response(
                status_code=400,  # Bad Request
                error_code="INVALID_BOOK_DATA",
                message=str(e),
                request=request
            )

        # Обработка технических исключений
        except BookServiceError as e:
            logger.error(f"Book service error: {e}", extra={"request_path": str(request.url.path)})
            return self._create_error_response(
                status_code=500,  # Internal Server Error
                error_code="SERVICE_ERROR",
                message="An error occurred while processing your request",
                request=request
            )

        except StorageError as e:
            logger.error(f"Storage error: {e}", extra={"request_path": str(request.url.path)})
            return self._create_error_response(
                status_code=503,  # Service Unavailable
                error_code="STORAGE_UNAVAILABLE",
                message="Data storage is temporarily unavailable",
                request=request
            )

        except (ApiClientError, MetadataClientError) as e:
            logger.error(f"External service error: {e}", extra={"request_path": str(request.url.path)})
            return self._create_error_response(
                status_code=503,  # Service Unavailable
                error_code="EXTERNAL_SERVICE_ERROR",
                message="External service is temporarily unavailable",
                request=request
            )

        except HTTPException:  # FastAPI HTTP исключения - пропускаем как есть
            raise

        except Exception as e:
            logger.error(
                f"Unexpected error: {e}",
                extra={
                    "request_path": str(request.url.path),
                    "traceback": traceback.format_exc()
                }
            )
            return self._create_error_response(
                status_code=500,  # Internal Server Error
                error_code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred",
                request=request
            )

    def _create_error_response(self, status_code: int, error_code: str, message: str, request: Request) -> JSONResponse:
        """Создает стандартизированный JSON ответ об ошибке"""

        request_id = get_request_id()

        error_response = {  # структура ошибки
            "error": {
                "code": error_code,
                "message": message,
                "request_id": request_id if request_id else None,
                "path": str(request.url.path)
            }
        }

        return JSONResponse(
            status_code=status_code,  # HTTP код ошибки
            content=error_response  # тело ответа с деталями ошибки
        )