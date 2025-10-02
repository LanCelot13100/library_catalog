import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv
from src.core.logger import get_logger
from src.models.sqlalchemy_models import Base

load_dotenv()

logger = get_logger(__name__)


DATABASE_URL = os.getenv("DATABASE_URL")  # получаем URL из .env
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")


DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "20"))

# Создание асинхронного движка SQLAlchemy
engine = create_async_engine(
    DATABASE_URL,
    future=True,
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Фабрика для создания асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии базы данных в FastAPI.
    Автоматически управляет транзакциями и закрытием сессии.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def create_tables():
    """Создает все таблицы в базе данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")


async def drop_tables():
    """Удаляет все таблицы из базы данных (осторожно!)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.warning("All database tables dropped")


async def check_db_connection() -> bool:
    """Проверяет подключение к базе данных"""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


async def close_db_connection():
    """Закрывает все соединения с базой данных"""
    await engine.dispose()
    logger.info("Database connections closed")