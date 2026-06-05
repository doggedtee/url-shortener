from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from schemas import URLRequest
from database import Base, engine, get_db
from models import URL
from shortener import generate_code

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "URL Shortener"}

@app.post("/shorten")
def shorten_url(data: URLRequest, db: Session = Depends(get_db)):
    code = generate_code()
    entry = URL(short_code=code, original_url=str(data.url))

    db.add(entry)
    db.commit()
    return {"original": data.url, "short": f"http://localhost:8000/{code}"}

@app.get("/{code}")
def redirect(code: str, db: Session = Depends(get_db)):
    entry = db.query(URL).filter(URL.short_code == code).first()
    if not entry:
        return {"error": "not found"}
    entry.clicks += 1
    db.commit()
    return RedirectResponse(entry.original_url)

@app.get("/{code}/stats")
def get_stats(code: str, db: Session = Depends(get_db)):
    entry = db.query(URL).filter(URL.short_code == code).first()
    if not entry:
        return {"error": "not found"}
    return {
        "short_code": entry.short_code,
        "original_url": entry.original_url,
        "clicks": entry.clicks
    }