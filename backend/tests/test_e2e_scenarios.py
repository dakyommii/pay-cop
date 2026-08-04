"""End-to-end acceptance tests for POST /payment/recommend (DESIGN.md §5, §9).

Each case is a fixed (input -> expected output) pair pinned against the
seeded catalog data (backend/scripts/seed.py). These exist to catch
regressions in the full request -> Rule Engine -> response pipeline, not to
prove the Rule Engine handles arbitrary inputs - that variety (실적 미충족,
혜택 없음, 결제수단 없음 등) is already covered by tests/test_rule_engine.py.
"""
import pytest

SCENARIOS = [
    pytest.param(
        {
            "merchant": "올리브영",
            "category": "뷰티",
            "amount": 48300,
            "cards": [
                {"name": "신한카드", "performance": 430000, "requiredPerformance": 300000}
            ],
            "payments": ["네이버페이", "카카오페이"],
        },
        {"card": "신한카드", "payment": "네이버페이", "saving": 5796},
        id="design-doc-scenario_shinhan-oliveyoung-naverpay",
    ),
    pytest.param(
        {
            "merchant": "GS칼텍스",
            "category": "주유",
            "amount": 100000,
            "cards": [
                {"name": "삼성카드", "performance": 600000, "requiredPerformance": 500000}
            ],
            "payments": [],
        },
        {"card": "삼성카드", "payment": None, "saving": 5000},
        id="samsung-gas-station_no-simple-pay",
    ),
    pytest.param(
        {
            "merchant": "배달의민족",
            "category": "배달앱",
            "amount": 30000,
            "cards": [
                {"name": "현대카드", "performance": 500000, "requiredPerformance": 400000},
                {"name": "신한카드", "performance": 430000, "requiredPerformance": 300000},
            ],
            "payments": ["카카오페이"],
        },
        {"card": "현대카드", "payment": "카카오페이", "saving": 3000},
        id="hyundai-delivery-app_irrelevant-card-ignored",
    ),
    pytest.param(
        {
            "merchant": "올리브영",
            "category": "뷰티",
            "amount": 48300,
            "cards": [
                {"name": "신한카드", "performance": 100000, "requiredPerformance": 300000}
            ],
            "payments": ["네이버페이"],
        },
        {"card": "신한카드", "payment": "네이버페이", "saving": 966},
        id="shinhan-performance-not-met_only-simple-pay-event-applies",
    ),
]


@pytest.mark.parametrize("payload,expected", SCENARIOS)
def test_recommend_pinned_scenario(client, payload, expected):
    resp = client.post("/payment/recommend", json=payload)
    assert resp.status_code == 200

    body = resp.json()
    assert body["recommendedCard"] == expected["card"]
    assert body["recommendedPayment"] == expected["payment"]
    assert body["expectedSaving"] == expected["saving"]
