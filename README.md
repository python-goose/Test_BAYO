
# Lead Management System
Микросервисная система для приема и обработки лидов (FastAPI + Redis + PostgreSQL).

## 🚀 Запуск проекта

Все сервисы упакованы в Docker. База данных инициализируется автоматически при старте.

```bash
# Сборка и запуск
sudo docker-compose up --build
````

---

## 🧪 Тестовые данные

При запуске контейнера автоматически инициализируется база данных и добавляются тестовые записи:
* **AFFILIATE** - 10
* **OFFER** - 100

Для удобного тестирования уже сгенерирован JWT токен для AFFILIATE с `id = 10`:

* **Auth Token (JWT):** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTB9.qhQkFErIHtFa7KGZEDVdTZGd6fP1qIOcapwmaDF8k7g`

Используйте этот токен для авторизации в API без необходимости вручную создавать пользователя и получать токен.

---

## 🧪 Тестирование (Data & Auth)

Для проверки работы API используйте предустановленные данные:

* **Auth Token (JWT):** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MTB9.qhQkFErIHtFa7KGZEDVdTZGd6fP1qIOcapwmaDF8k7g`
* **Offer ID:** `100`
* **Valid Countries (ISO):** `UA`, `PL`, `DE`, `US`

### 1. Прием лида (Landings API)

**URL:** [http://localhost:8000/docs](http://localhost:8000/docs)

1. Нажать **Authorize**, вставить токен.
2. Отправить POST на `/leads/` с `offer_id: 100` и валидной страной. Лид упадет в Redis.

### 2. Проверка заказов (Core API)

**URL:** [http://localhost:8001/docs](http://localhost:8001/docs)

1. Нажать **Authorize**, вставить токен.
2. Использовать GET методы для просмотра лидов, сохраненных воркером в БД.

---


## 🏗 Стек

FastAPI, SQLAlchemy (Async), Redis, PostgreSQL, Docker Compose.

