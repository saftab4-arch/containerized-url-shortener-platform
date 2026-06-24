import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from app import app


def test_home_endpoint():
    client = app.test_client()
    response = client.get("/")

    assert response.status_code == 200
    data = response.get_json()
    assert data["service"] == "Containerized URL Shortener Platform"
    assert data["version"] == "v1"


def test_health_endpoint():
    client = app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"


def test_shorten_missing_url():
    client = app.test_client()
    response = client.post("/shorten", json={})

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Missing url field"
