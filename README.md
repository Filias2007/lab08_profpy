# Lab 08: Network & Asynchronous Programming. REST API (Variant 3)

Асинхронний REST API сервіс для системи «Інтернет-магазин» (E-Commerce Processing System), побудований на базі FastAPI, Pydantic, SQLAlchemy, HTTPX та asyncio.

---

## 🏗️ Архітектура проєкту

Застосунок побудовано відповідно до багаторівневої архітектури:
**HTTP Client / Swagger UI ➔ FastAPI REST API ➔ Pydantic Schemas ➔ Service Layer ➔ Repository Layer ➔ SQLite Database**

### Структура каталогів:
- `src/shop/` — основний код застосунку:
  - `api.py` — FastAPI REST API ендпоінти.
  - `schemas.py` — Pydantic-моделі валідації та серіалізації даних.
  - `models.py` — ORM-моделі SQLAlchemy (`Product`, `Category`).
  - `database.py` — налаштування підключення до бази даних SQLite та генератор сесій.
  - `repositories.py` — паттерн Repository для роботи з БД.
  - `services.py` — транзакційна бізнес-логіка покупок та обчислень.
  - `external_api.py` — асинхронні мережеві запити (`httpx.AsyncClient`, `asyncio.Semaphore`, `Retry`, `Timeout`, `Tasks`, `gather`).
  - `exceptions.py` — кастомні винятки предметної області.
  - `config.py` — конфігурація та змінні оточення.
- `tests/` — автоматизований тестовий набір:
  - `conftest.py` — спільні фікстури Pytest та ізольована тестова БД в пам'яті (`sqlite:///:memory:`).
  - `test_api.py` — інтеграційні тести REST API ендпоінтів (`TestClient`, `httpx.AsyncClient`).
  - `test_external.py` — тести асинхронних мережевих операцій (паралелізм, семафори, retry, timeout).

---

## 🌐 Опис REST API Endpoints

| Метод | Endpoint | Опис | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/products` | Отримання списку товарів (з фільтрацією за `category_id`) | `200 OK` |
| `GET` | `/products/{id}` | Отримання деталей товару за Path Parameter | `200 OK` / `404 Not Found` |
| `POST` | `/products` | Створення нового товару з Pydantic-валідацією | `201 Created` / `422 Error` |
| `PATCH` | `/products/{id}` | Часткове оновлення ціни, кількості або категорії | `200 OK` / `404 Not Found` |
| `DELETE` | `/products/{id}` | Видалення товару з каталогу | `204 No Content` / `404 Not Found` |
| `GET` | `/categories/{id}/products` | Отримання товарів конкретної категорії | `200 OK` / `404 Not Found` |
| `POST` | `/products/{id}/purchase` | Тразакційне оформлення покупки товару | `200 OK` / `400 Bad Request` |
| `POST` | `/products/batch-fetch` | Асинхронне пакетне завантаження товарів із таймаутом | `200 OK` / `504 Timeout