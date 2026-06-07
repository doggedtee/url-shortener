from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from schemas import URLRequest
from database import Base, engine, get_db
from models import URL
from shortener import generate_code
from datetime import datetime, timezone, timedelta
from cache import r

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "URL Shortener"}

@app.post("/shorten")
def shorten_url(data: URLRequest, db: Session = Depends(get_db)):
    code = generate_code()
    expires_at = None
    if data.expires_in_days:
        expires_at = datetime.now(timezone.utc) + timedelta(days=data.expires_in_days)
    entry = URL(short_code=code, original_url=str(data.url), expires_at=expires_at)

    db.add(entry)
    db.commit()
    return {"original": data.url, "short": f"http://localhost:8000/{code}"}

@app.get("/{code}")
def redirect(code: str, db: Session = Depends(get_db)):
    cached = r.get(code)
    if cached:
        return RedirectResponse(cached)
    
    entry = db.query(URL).filter(URL.short_code == code).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Short code not found")
    if entry.expires_at and entry.expires_at < datetime.now():
        raise HTTPException(status_code=410, detail="Link has expired")
    entry.clicks += 1
    db.commit()
    r.set(code, entry.original_url)
    return RedirectResponse(entry.original_url)

@app.get("/{code}/stats")
def get_stats(code: str, db: Session = Depends(get_db)):
    entry = db.query(URL).filter(URL.short_code == code).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Short code not found")
    return {
        "short_code": entry.short_code,
        "original_url": entry.original_url,
        "clicks": entry.clicks
    }