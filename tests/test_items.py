from starlette import status


def test_create_item(client):
    payload = {"text": "hello world", "is_active": True}

    response = client.post("/items/", json=payload)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == 1
    assert data["text"] == "hello world"
    assert data["is_active"] is True


def test_list_items(client):
    client.post("/items/", json={"text": "item 1"})
    client.post("/items/", json={"text": "item 2"})

    response = client.get("/items/list?limit=10")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    texts = [item["text"] for item in data]

    assert "item 1" in texts
    assert "item 2" in texts


def test_get_item_by_id(client):
    create_resp = client.post("/items/", json={"text": "single item"})
    item_id = create_resp.json()["id"]

    response = client.get(f"/items/{item_id}")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["id"] == item_id
    assert data["text"] == "single item"


def test_get_item_not_found(client):
    response = client.get("/items/9999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Item not found"
