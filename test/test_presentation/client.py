from fastapi.testclient import TestClient

from app.main.app import app

client = TestClient(app)