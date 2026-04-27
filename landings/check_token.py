import os
import jwt
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

# Генерируем токен для affiliate_id = 10
token = jwt.encode({"id": 10}, SECRET_KEY, algorithm=ALGORITHM)
print(token)

# python landings/check_token.py
# Если нужно получить токен для указанного айдишника