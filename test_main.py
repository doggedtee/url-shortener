from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "URL Shortener"}

def test_shorten_valid_url():
    response = client.post("/shorten", json={"url": "https://example.com"})
    assert response.status_code == 200
    assert "short" in response.json()

def test_shorten_invalid_url():
    response = client.post("/shorten", json={"url": "not-a-url"})
    assert response.status_code == 422

def test_redirect_not_found():
    response = client.get("/fakecode123", follow_redirects=False)
    assert response.status_code == 404

