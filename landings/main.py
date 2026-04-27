import os
import jwt
import json
import redis
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Загружаем переменные из .env
load_dotenv()

app = FastAPI()

# Настройки JWT
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
security = HTTPBearer()

# Настройки Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
REDIS_DB = os.getenv("REDIS_DB", 0)

# Указываем папку с шаблонами
templates = Jinja2Templates(directory="landings/templates")

# Константные значения 
EXPECTED_OFFER_ID = 100 # Айдишник товара
EXPECTED_AFFILIATE_ID = 10 # Айдишник афилиата
EXPECTED_COUNTRY_CODES = ["UA", "PL", "DE", "US"] # Доступные страны на выбор

# Инициализация клиента Redis
# decode_responses=True позволяет получать строки вместо байтов
redis_client = redis.Redis(
    host=REDIS_HOST, 
    port=int(REDIS_PORT), 
    db=int(REDIS_DB), 
    decode_responses=True
)

# Проверка токена на входе
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Невалидный токен!")


#@app.get("/", response_class=HTMLResponse)
#def read_root(request: Request):
    #return templates.TemplateResponse(request=request, name="index.html")


@app.post("/lead")
def add_lead(
    name: str = Form(...),
    phone: str = Form(...),
    country: str = Form(...),
    offer_id: int = Form(...),
    token_data: dict = Depends(verify_token)
):
    # Достаем ID из токена для удобства
    aff_id_from_token = token_data.get("id")
    
    # 0. Проверка соответствия аффилиата (токен vs константа)
    # Можно было бы делать проверку с БД, но как я понял процесс Сервіс 1 не должен знать о Сервисе 2
    if aff_id_from_token != EXPECTED_AFFILIATE_ID:
        raise HTTPException(status_code=403, detail="Affiliate ID mismatch!")
    
    # 1. Валидация констант (защита от подмены в HTML)
    if offer_id != EXPECTED_OFFER_ID:
        raise HTTPException(status_code=400, detail="Invalid offer_id")
    
    # 2. Валидация страны (проверка по списку разрешенных)
    if country not in EXPECTED_COUNTRY_CODES:
        raise HTTPException(status_code=400, detail="Invalid country code")

    # 3. Валидация данных пользователя
    # Проверка имени (не пустое и не слишком короткое)
    if len(name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Name is too short")
    
    # Проверка телефона (базовая: должен содержать только цифры и +, минимум 10 символов)
    clean_phone = phone.replace(" ", "").replace("-", "")
    if not (clean_phone.startswith('+') or clean_phone.isdigit()) or len(clean_phone) < 10:
        raise HTTPException(status_code=400, detail="Invalid phone format")
    
    # --- ЛОГИКА REDIS ---
    # Формируем объект лида для очереди
    lead_payload = {
        "name": name,
        "phone": clean_phone,
        "country": country,
        "offer_id": offer_id,
        "affiliate_id": aff_id_from_token
    }

    try:
        # Сериализуем в JSON и пушим в список leads_queue
        redis_client.rpush("leads_queue", json.dumps(lead_payload))
    except redis.ConnectionError:
        # Если Redis не запущен, отдаем 500 ошибку
        raise HTTPException(status_code=500, detail="System error: Queue is unavailable")


    # Вывод в консоль только если валидация прошла
    print(f"Успех! Данные от аффилиата {aff_id_from_token} приняты.")
    return {"status": 200}