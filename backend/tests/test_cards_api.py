def test_card_registration_flow(client):
    resp = client.post("/users", json={"name": "테스트유저"})
    assert resp.status_code == 201
    user_id = resp.json()["id"]

    resp = client.post(
        f"/users/{user_id}/cards",
        json={
            "card_name": "신한카드",
            "card_type": "신용카드",
            "current_performance": 100000,
            "required_performance": 300000,
        },
    )
    assert resp.status_code == 201
    card = resp.json()
    assert card["card_name"] == "신한카드"

    resp = client.get(f"/users/{user_id}/cards")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp = client.patch(
        f"/users/{user_id}/cards/{card['id']}/performance",
        json={"current_performance": 430000},
    )
    assert resp.status_code == 200
    assert resp.json()["current_performance"] == 430000


def test_card_registration_unknown_user_returns_404(client):
    resp = client.post(
        "/users/999999/cards",
        json={"card_name": "신한카드", "card_type": "신용카드"},
    )
    assert resp.status_code == 404


def test_performance_update_unknown_card_returns_404(client):
    resp = client.post("/users", json={"name": "유저"})
    user_id = resp.json()["id"]

    resp = client.patch(
        f"/users/{user_id}/cards/999999/performance",
        json={"current_performance": 1000},
    )
    assert resp.status_code == 404


def test_card_creation_rejects_negative_performance(client):
    resp = client.post("/users", json={"name": "유저"})
    user_id = resp.json()["id"]

    resp = client.post(
        f"/users/{user_id}/cards",
        json={"card_name": "신한카드", "card_type": "신용카드", "current_performance": -1},
    )
    assert resp.status_code == 422
