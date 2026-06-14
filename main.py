from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from schemas import URLRequest
from database import Base, engine, get_db
from models import URL
from shortener import generate_code
from datetime import datetime, timezone, timedelta
from cache import r
from tasks import check_url
from logger import logger
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/")
def root():
    return {"message": "URL Shortener"}

@app.post("/shorten")
@limiter.limit("5/minute")
def shorten_url(request: Request, data: URLRequest, db: Session = Depends(get_db)):
    code = generate_code()
    expires_at = None
    if data.expires_in_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=data.expires_in_days)
    entry = URL(short_code=code, original_url=str(data.url), expires_at=expires_at)
    db.add(entry)
    db.commit()
    check_url.delay(str(data.url), code)
    logger.info(f"Created short URL: {code} -> {data.url}")
    return {"original": data.url, "short": f"http://localhost:8000/{code}"}

@app.get("/{code}")
def redirect(code: str, db: Session = Depends(get_db)):
    cached = r.get(code)
    if cached:
        logger.info(f"Cache hit: {code}")
        return RedirectResponse(cached)
    
    entry = db.query(URL).filter(URL.short_code == code).first()
    if not entry:
        logger.warning(f"Short code not found: {code}")
        raise HTTPException(status_code=404, detail="Short code not found")
    if entry.expires_at and entry.expires_at < datetime.now():
        logger.warning(f"Expired link accessed: {code}")
        raise HTTPException(status_code=410, detail="Link has expired")
    entry.clicks += 1
    db.commit()
    r.set(code, entry.original_url)
    logger.info(f"Redirect: {code} -> {entry.original_url}")
    return RedirectResponse(entry.original_url)

@app.get("/{code}/stats")
def get_stats(code: str, db: Session = Depends(get_db)):
    entry = db.query(URL).filter(URL.short_code == code).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Short code not found")
    return {
        "short_code": entry.short_code,
        "original_url": entry.original_url,
        "clicks": entry.clicks,
        "is_reachable": entry.is_reachable
    }