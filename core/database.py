import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Создаем асинхронный движок для работы с Postgres
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем фабрику сессий (через них будем делать запросы)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Базовый класс для всех наших моделей
class Base(DeclarativeBase):
    pass