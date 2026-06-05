from fastapi import FastAPI
from pydantic import BaseModel
from shortener import generate_code

app = FastAPI()

class URLRequest(BaseModel):
    url: str

@app.get("/")
def root():
    return {"message": "URL Shortener"}

@app.post("/shorten")
def shorten_url(data: URLRequest):
    code = generate_code()
    return {"original": data.url, "short": f"http://localhost:8000/{code}"}