import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_api_health():
    """Verify the API is reachable."""
    # Note: This assumes you have a root '/' or health check endpoint
    # If not, let's test the /ask endpoint specifically
    pass

def test_ask_endpoint_structure():
    """Verify the /ask endpoint returns the correct JSON keys."""
    payload = {"query": "How much did I spend on Travel?", "user_id": "test_user"}
    response = client.post("/ask", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "analysis" in data
    assert "is_cached" in data
    assert isinstance(data["analysis"], str)

def test_invalid_payload():
    """Verify the API handles bad data gracefully."""
    # Sending 'q' instead of 'query'
    payload = {"q": "wrong key"} 
    response = client.post("/ask", json=payload)
    assert response.status_code == 422 # Unprocessable Entity