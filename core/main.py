import os
from datetime import datetime, date
from typing import Optional, List

import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession


from core.database import AsyncSessionLocal
from core.models import Lead, Affiliate


# Загружаем настройки
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

app = FastAPI(title="Core Analytics API")
security = HTTPBearer()

# --- Зависимости ---

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_affiliate(
    auth: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """
    Проверка Bearer токена и существования аффилиата в БД
    """
    try:
        # Декодируем токен
        payload = jwt.decode(auth.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        # ТЗ подразумевает, что ID аффилиата лежит в поле "id"
        affiliate_id = payload.get("id")
        
        if affiliate_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Токен не содержит ID пользователя"
            )
        
        # Проверка: есть ли такой аффилиат в таблице affiliates
        query = select(Affiliate).where(Affiliate.id == int(affiliate_id))
        result = await db.execute(query)
        affiliate = result.scalar_one_or_none()
        
        if not affiliate:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Доступ запрещен: аффилиат не найден в базе"
            )
            
        return affiliate
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Невалидный или просроченный токен"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Ошибка сервера: {str(e)}"
        )

# --- Эндпоинты ---

@app.get("/leads")
async def get_leads(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    group_by: Optional[str] = Query(None, regex="^(date|offer)$"),
    db: AsyncSession = Depends(get_db),
    current_user: Affiliate = Depends(get_current_affiliate) # Защита включена
):
    """
    Получение лидов с фильтрацией, группировкой и проверкой доступа
    """
    # Базовый запрос
    query = select(Lead)

    # 1. Фильтрация по датам
    if date_from:
        query = query.where(Lead.created_at >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.where(Lead.created_at <= datetime.combine(date_to, datetime.max.time()))

    # 2. Группировка
    if group_by == "date":
        date_col = func.date(Lead.created_at)
        query = select(date_col, func.count(Lead.id)).group_by(date_col)
    elif group_by == "offer":
        query = select(Lead.offer_id, func.count(Lead.id)).group_by(Lead.offer_id)

    result = await db.execute(query)
    
    if group_by:
        rows = result.all()
        return [{"group": str(row[0]), "count": row[1]} for row in rows]
    
    leads = result.scalars().all()
    return leads
