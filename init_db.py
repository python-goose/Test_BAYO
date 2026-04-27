import asyncio
from sqlalchemy import select
from core.database import engine, Base, AsyncSessionLocal
from core.models import Affiliate, Offer, Lead

async def init_db():
    # ШАГ 1: Создание таблиц (всегда выполняется)
    async with engine.begin() as conn:
        print("Проверка и создание таблиц...")
        await conn.run_sync(Base.metadata.create_all)
    print("Таблицы готовы.")

    # ШАГ 2: Вставка тестовых данных
    # Если данные не нужны — просто закомментируй вызов функции ниже
    await insert_test_data()

async def insert_test_data():
    async with AsyncSessionLocal() as session:
        print("Проверка наличия тестовых данных...")
        
        # Проверяем Аффилиата
        res_aff = await session.execute(select(Affiliate).where(Affiliate.id == 10))
        if not res_aff.scalar_one_or_none():
            session.add(Affiliate(id=10, name="Yurii Admin"))
            print("Аффилиат ID: 10 добавлен.")

        # Проверяем Оффер
        res_off = await session.execute(select(Offer).where(Offer.id == 100))
        if not res_off.scalar_one_or_none():
            session.add(Offer(id=100, name="Super Offer"))
            print("Оффер ID: 100 добавлен.")
        
        try:
            await session.commit()
            print("--- Тестовые данные инициализированы ---")
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при вставке данных: {e}")

if __name__ == "__main__":
    asyncio.run(init_db())