from fastapi.testclient import TestClient

from main.app import app

client = TestClient(app)