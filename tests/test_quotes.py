import pytest

def test_random_quote(client):
    response = client.get("/quote/random")
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert "author" in data
    assert "category" in data

def test_random_quote_by_category(client):
    response = client.get("/quote/random?category=Мотивация")
    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "Мотивация"

def test_random_quote_invalid_category(client):
    response = client.get("/quote/random?category=Несуществующая")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data

def test_quote_by_id(client):
    response = client.get("/quote/1")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["id"] == 1

def test_quote_by_id_not_found(client):
    response = client.get("/quote/99999")
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
