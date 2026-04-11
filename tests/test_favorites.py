import uuid

def test_add_favorite(client):
    session_id = str(uuid.uuid4())
    response = client.post("/favorites/add", json={
        "quote_id": 1,
        "session_id": session_id
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True

def test_add_favorite_duplicate(client):
    session_id = str(uuid.uuid4())
    client.post("/favorites/add", json={
        "quote_id": 1,
        "session_id": session_id
    })
    response = client.post("/favorites/add", json={
        "quote_id": 1,
        "session_id": session_id
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == False
    assert "уже" in data["message"] or "already" in data["message"]

def test_get_favorites(client):
    session_id = str(uuid.uuid4())
    client.post("/favorites/add", json={
        "quote_id": 1,
        "session_id": session_id
    })
    response = client.get(f"/favorites/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert "favorites" in data
    assert len(data["favorites"]) >= 1

def test_check_favorite(client):
    session_id = str(uuid.uuid4())
    client.post("/favorites/add", json={
        "quote_id": 1,
        "session_id": session_id
    })
    response = client.get(f"/favorites/check/1/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["is_favorite"] == True
