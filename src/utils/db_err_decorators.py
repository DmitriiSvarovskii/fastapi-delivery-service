import logging
from functools import wraps

from fastapi import HTTPException, status
from sqlalchemy.exc import (
    IntegrityError,
    StatementError,
    OperationalError,
    DBAPIError,
)

logger = logging.getLogger(__name__)


def handle_db_errors(func):
    """
    Декоратор для обработки ошибок SQLAlchemy:

    - StatementError   → 400 Bad Request
    - IntegrityError  → 409 Conflict
    - OperationalError → 503 Service Unavailable
    - DBAPIError      → 500 Internal Server Error
    - прочие исключения → 500 Internal Server Error
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return result

        except StatementError:
            logger.exception("Statement error occurred", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request data"
            )

        except IntegrityError:
            logger.exception("Integrity constraint violated", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Conflict: resource already \
                    exists or violates constraint"
            )

        except OperationalError:
            logger.exception(
                "Operational error (e.g., database unavailable)",
                exc_info=True
            )
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service temporarily unavailable"
            )

        except DBAPIError:
            logger.exception("General database error", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal database error"
            )

        except HTTPException:
            raise

        except Exception:
            logger.exception("Unexpected error in DB layer", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    return wrapper
