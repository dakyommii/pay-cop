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


def test_recommend_admits_no_benefit_instead_of_faking_one(client):
    # 카드 등록 화면에서 구체적인 상품명(예: "신한카드 Deep Oil")을 고르면 이슈어 단위
    # Benefit 카탈로그와 매칭되지 않는다 (의도된 동작 - docs/... cardCatalog.ts 참고).
    # 매칭되는 매장/이벤트도 없는 경우, "이게 최선"인 척 포장하지 않고 혜택이 없다고
    # 정직하게 답해야 한다.
    resp = client.post(
        "/payment/recommend",
        json={
            "merchant": "이마트",
            "category": "마트",
            "amount": 50000,
            "cards": [
                {"name": "신한카드 Deep Oil", "performance": 500000, "requiredPerformance": 300000}
            ],
            "payments": ["네이버페이"],
        },
    )
    assert resp.status_code == 200

    body = resp.json()
    assert body["expectedSaving"] == 0
    assert "혜택이 없습니다" in body["reason"]
    assert "가장 유리합니다" not in body["reason"]
