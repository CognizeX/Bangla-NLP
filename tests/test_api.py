from fastapi.testclient import TestClient
from app.app import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200