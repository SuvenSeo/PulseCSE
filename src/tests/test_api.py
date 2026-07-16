import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database import database

client = TestClient(app)

def test_api_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_api_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "metrics" in response.json()

def test_api_metrics_prom():
    response = client.get("/metrics.prom")
    assert response.status_code == 200
    assert "metrics" in response.text

def test_api_dashboard():
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    assert "dashboard" in response.json()

def test_api_alerts():
    response = client.get("/api/alerts")
    assert response.status_code == 200
    assert "alerts" in response.json()

def test_api_portfolio():
    response = client.get("/api/portfolio")
    assert response.status_code == 200
    assert "portfolio" in response.json()

def test_api_watchlist():
    response = client.get("/api/watchlist")
    assert response.status_code == 200
    assert "watchlist" in response.json()

@pytest.mark.asyncio
async def test_database_connection():
    await database.connect()
    assert database.is_connected
    await database.disconnect()
    assert not database.is_connected