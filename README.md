# URL Shortener

A URL shortener API built with FastAPI, SQLite, Redis, and Celery.

## Features
- Shorten URLs
- Redirect to original URL
- Click tracking
- Link expiry
- Redis caching
- Background URL reachability check via Celery
- Rate limiting (5 requests/minute)
- CORS
- Health check endpoint

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

## Environment

Create a `.env` file:

```
DATABASE_URL=sqlite:///./urls.db
REDIS_URL=redis://localhost:6379/0
```

## Run

```bash
# Start Redis
docker start redis

# Start FastAPI
uvicorn main:app --reload

# Start Celery worker
python -m celery -A tasks worker --pool=solo
```

## Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | /shorten | Create short URL |
| GET | /{code} | Redirect to original |
| GET | /{code}/stats | View click stats |
| GET | /health | Health check |

## Run Tests

```bash
pytest test_main.py -v
```
