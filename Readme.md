
```md
# 📦 Botgauge Key-Value REST API

A production-ready **Key-Value REST API** built using **FastAPI** with **Django ORM** and **PostgreSQL**, including **rate limiting** and a **fault-tolerant Python client**.

---

## 🚀 Features

- FastAPI-based REST API
- Data persistence using Django ORM
- PostgreSQL database
- Full CRUD support
- Pagination support
- Per-client rate limiting (60 req/min)
- Production-grade Python client with:
  - Retries
  - Exponential backoff
  - Jitter
  - Proper HTTP 429 handling
- Safe retry behavior (no duplicate data)

---

## 🏗️ Architecture

```

Python Client → FastAPI → Django ORM → PostgreSQL

```

- **FastAPI** handles HTTP requests
- **Django ORM** manages database access and migrations
- **PostgreSQL** stores key-value data
- ORM calls are executed in a thread pool to keep the event loop non-blocking

---

## 📂 Project Structure

```

Botgauge/
├── app/
│   └── main.py            # FastAPI application
├── dbcore/
│   ├── dbcore/            # Django settings
│   ├── kvstore/           # Django app (Item model)
│   └── manage.py
├── client/
│   └── kv_client.py       # Production-grade Python client
├── venv/
└── README.md

````

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone <your-repo-url>
cd Botgauge
````

---

### 2️⃣ Create and activate virtual environment

```bash
python -m venv venv
source venv/bin/activate
```

---

### 3️⃣ Install dependencies

```bash
pip install fastapi uvicorn django psycopg2-binary slowapi requests python-dotenv
```

---

### 4️⃣ Configure PostgreSQL

Create a database and user:

```sql
CREATE DATABASE botgauge_db;
CREATE USER botgauge_user WITH PASSWORD 'botgauge_user';
GRANT ALL PRIVILEGES ON DATABASE botgauge_db TO botgauge_user;
```

Grant table permissions:

```sql
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO botgauge_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO botgauge_user;
```

---

### 5️⃣ Run Django migrations

```bash
cd dbcore
python manage.py migrate
```

---

### 6️⃣ Start the FastAPI server

From the project root:

```bash
uvicorn app.main:app --reload
```

Server runs at:

```
http://127.0.0.1:8000
```

API docs:

```
http://127.0.0.1:8000/docs
```

---

## 📌 API Endpoints

### Create item

```
POST /items/
Body: { "key": "example", "value": "data" }
```

### Get item

```
GET /items/{key}
```

### Update item

```
PUT /items/{key}?value=new_value
```

### Delete item

```
DELETE /items/{key}
```

### List items (pagination)

```
GET /items/?page=1&page_size=10
```

---

## ⏱️ Rate Limiting

* **60 requests per minute per client**
* Applies to all `/items/*` endpoints
* Returns **HTTP 429** when exceeded

---

## 🧪 Example cURL Tests

```bash
curl -X POST http://127.0.0.1:8000/items/ \
  -H "Content-Type: application/json" \
  -d '{"key":"app_name","value":"KeyValue REST API"}'
```

```bash
curl http://127.0.0.1:8000/items/app_name
```

---

## 🧠 Python Client Usage

```python
from client.kv_client import KVClient

client = KVClient("http://127.0.0.1:8000")

client.create("hello", "world")
client.get("hello")
client.update("hello", "updated")
client.list(page=1, page_size=5)
client.delete("hello")
```

### Client Features

* Automatic retries
* Exponential backoff
* Jitter to avoid request bursts
* Safe handling of HTTP 429
* Graceful failure after retry budget

---

## 🔐 Idempotency & Safety

* Unique keys enforced at the database level
* Retried POST requests do not create duplicates
* PUT and DELETE operations are idempotent
* Client retries are safe and consistent

---

## ✅ Requirements Checklist

* [x] FastAPI REST API
* [x] Django ORM persistence
* [x] PostgreSQL database
* [x] CRUD operations
* [x] Pagination
* [x] Rate limiting (60 req/min)
* [x] HTTP 429 handling
* [x] Production-grade Python client
* [x] Exponential backoff & jitter
* [x] Fault tolerance & safety

---

## Conclusion

This project demonstrates a **real-world backend system** with proper API design, database integration, rate limiting, and a resilient client. The architecture and implementation follow production best practices.

````

---

