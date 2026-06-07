from celery import Celery
import httpx
from database import SessionLocal
from models import URL

celery = Celery("tasks", broker="redis://localhost:6379/0")

@celery.task
def check_url(url: str, short_code: str):
    try:
        response = httpx.get(url, timeout=5)
        reachable = response.status_code < 400
    except Exception:
        reachable = False

    db = SessionLocal()
    try:
        entry = db.query(URL).filter(URL.short_code == short_code).first()
        if entry:
            entry.is_reachable = reachable
            db.commit()
    finally:
        db.close()
    print(f"{short_code} -> {url} -> reachable: {reachable}")