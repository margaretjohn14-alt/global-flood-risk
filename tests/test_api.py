"""
Basic tests for the API.
These run in the CI pipeline before deployment.
If they fail, the deployment is blocked.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200

def test_risk_default_weights():
    response = client.get("/risk")
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) > 100  # should have ~180 countries

def test_risk_custom_weights():
    response = client.get("/risk?w_hazard=0.8&w_vuln=0.1&w_coping=0.1")
    assert response.status_code == 200

def test_country_lookup():
    response = client.get("/country/DEU")  # Germany
    assert response.status_code == 200
    data = response.json()
    assert data["iso3"] == "DEU"
    assert "risk_score" in data

def test_country_not_found():
    response = client.get("/country/XXX")
    assert response.status_code == 200
    assert "error" in response.json()