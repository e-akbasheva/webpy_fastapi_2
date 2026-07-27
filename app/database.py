from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import config
from sqlalchemy.orm import declarative_base
import logging

logger = logging.getLogger(__name__)

engine = create_async_engine(config.DATABASE_URL, echo=True)

Session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db_session(): # -> AsyncSession
    logger.info("Creating database session")
    async with Session() as session:
        try:
            logger.info("Yielding session")
            yield session
        finally:
            logger.info("Closing session")
            await session.close()


Base = declarative_base()