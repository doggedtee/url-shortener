from celery import Celery
import httpx

celery = Celery("tasks", broker="redis://localhost:6379/0")

@celery.task
def check_url(url: str, short_code: str):
    try:
        response = httpx.get(url, timeout=5)
        reachable = response.status_code < 400
    except Exception:
        reachable = False
    print(f"{short_code} -> {url} -> reachable: {reachable}")