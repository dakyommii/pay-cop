def test_recommend_reproduces_design_doc_scenario(client):
    resp = client.post(
        "/payment/recommend",
        json={
            "merchant": "올리브영",
            "category": "뷰티",
            "amount": 48300,
            "cards": [
                {"name": "신한카드", "performance": 430000, "requiredPerformance": 300000}
            ],
            "payments": ["네이버페이", "카카오페이"],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["recommendedCard"] == "신한카드"
    assert body["recommendedPayment"] == "네이버페이"
    assert body["expectedSaving"] == 5796
    assert "신한카드" in body["reason"]
    assert "네이버페이" in body["reason"]

    assert len(body["candidates"]) == 2
    top_candidate = body["candidates"][0]
    assert top_candidate["cardName"] == "신한카드"
    assert top_candidate["paymentType"] == "네이버페이"
    assert top_candidate["expectedSaving"] == 5796


def test_recommend_without_required_performance_field_matches_example_payload(client):
    # DESIGN.md §11's example payload omits requiredPerformance entirely.
    resp = client.post(
        "/payment/recommend",
        json={
            "merchant": "올리브영",
            "category": "뷰티",
            "amount": 48300,
            "cards": [{"name": "신한카드", "performance": 430000}],
            "payments": ["네이버페이"],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    # required_performance defaults to 0, so the performance condition is met
    # and the benefit still applies.
    assert body["recommendedCard"] == "신한카드"
    assert body["expectedSaving"] == 5796


def test_recommend_missing_merchant_returns_422(client):
    resp = client.post(
        "/payment/recommend",
        json={"category": "뷰티", "amount": 48300, "cards": [{"name": "신한카드", "performance": 0}]},
    )
    assert resp.status_code == 422


def test_recommend_non_positive_amount_returns_422(client):
    resp = client.post(
        "/payment/recommend",
        json={
            "merchant": "올리브영",
            "category": "뷰티",
            "amount": 0,
            "cards": [{"name": "신한카드", "performance": 0}],
        },
    )
    assert resp.status_code == 422


def test_recommend_empty_cards_returns_422(client):
    resp = client.post(
        "/payment/recommend",
        json={"merchant": "올리브영", "category": "뷰티", "amount": 48300, "cards": []},
    )
    assert resp.status_code == 422
