import os
import json
import asyncio
from datetime import datetime, timedelta
from dotenv import load_dotenv

import redis.asyncio as redis
from sqlalchemy import select
from core.database import AsyncSessionLocal
from core.models import Lead

# Загружаем переменные из .env
load_dotenv()

# Настройки Redis из твоего файла
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

async def start_worker():
    # Создаем URL для подключения к Redis на основе твоего .env
    redis_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    client = redis.from_url(redis_url, decode_responses=True)
    
    print(f"--- Воркер запущен ---")
    print(f"Подключение к Redis: {REDIS_HOST}:{REDIS_PORT} (DB: {REDIS_DB})")
    print("Ожидание новых лидов в очереди 'leads_queue'...")

    while True:
        # Ждем появления данных в очереди
        result = await client.blpop("leads_queue", timeout=0)
        
        if result:
            _, lead_json = result
            lead_data = json.loads(lead_json)
            
            async with AsyncSessionLocal() as session:
                # 1. Проверка на дубликат за последние 10 минут
                time_limit = datetime.utcnow() - timedelta(minutes=10)
                
                query = select(Lead).where(
                    Lead.phone == lead_data['phone'],
                    Lead.name == lead_data['name'],
                    Lead.offer_id == lead_data['offer_id'],
                    Lead.affiliate_id == lead_data['affiliate_id'],
                    Lead.created_at >= time_limit
                )
                
                check = await session.execute(query)
                is_duplicate = check.scalar_one_or_none()

                if is_duplicate:
                    print(f"--- ДУБЛИКАТ: {lead_data['phone']} (Пропускаем)")
                    continue

                # 2. Запись в PostgreSQL
                new_lead = Lead(
                    name=lead_data['name'],
                    phone=lead_data['phone'],
                    country=lead_data['country'],
                    offer_id=lead_data['offer_id'],
                    affiliate_id=lead_data['affiliate_id']
                )
                
                session.add(new_lead)
                await session.commit()
                print(f"+++ УСПЕХ: Лид {lead_data['name']} ({lead_data['phone']}) записан в БД")

if __name__ == "__main__":
    try:
        asyncio.run(start_worker())
    except KeyboardInterrupt:
        print("\nВоркер остановлен.")