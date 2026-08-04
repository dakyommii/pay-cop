from app.services.rule_engine import CardInput, build_candidates


def test_design_doc_scenario_recommends_shinhan_and_naverpay(db):
    # DESIGN.md §5 시나리오: 올리브영 48,300원, 신한카드 실적 430,000원(기준 300,000원),
    # 네이버페이/카카오페이 보유 -> 신한카드+네이버페이, 절약 5,796원이 1순위여야 한다.
    candidates = build_candidates(
        db,
        merchant="올리브영",
        category="뷰티",
        amount=48300,
        cards=[CardInput(name="신한카드", performance=430000, required_performance=300000)],
        payments=["네이버페이", "카카오페이"],
    )

    top = candidates[0]
    assert top.card_name == "신한카드"
    assert top.payment_type == "네이버페이"
    assert top.discount_amount == 4830
    assert top.event_amount == 966
    assert top.total_saving == 5796

    kakao_candidate = next(c for c in candidates if c.payment_type == "카카오페이")
    assert kakao_candidate.event_amount == 0
    assert kakao_candidate.total_saving == 4830


def test_benefit_not_applied_when_performance_not_met(db):
    candidates = build_candidates(
        db,
        merchant="올리브영",
        category="뷰티",
        amount=48300,
        cards=[CardInput(name="신한카드", performance=100000, required_performance=300000)],
        payments=["네이버페이"],
    )

    candidate = candidates[0]
    assert candidate.performance_met is False
    assert candidate.discount_amount == 0
    # simple-pay event benefit is independent of card performance
    assert candidate.event_amount == 966
    assert candidate.total_saving == 966


def test_no_matching_benefit_yields_zero_discount(db):
    candidates = build_candidates(
        db,
        merchant="올리브영",
        category="뷰티",
        amount=48300,
        cards=[CardInput(name="존재하지않는카드", performance=1000000, required_performance=0)],
        payments=["네이버페이"],
    )

    candidate = candidates[0]
    assert candidate.benefit_category is None
    assert candidate.discount_amount == 0
    assert candidate.event_amount == 966


def test_no_payments_falls_back_to_none_option(db):
    candidates = build_candidates(
        db,
        merchant="올리브영",
        category="뷰티",
        amount=48300,
        cards=[CardInput(name="신한카드", performance=430000, required_performance=300000)],
        payments=[],
    )

    assert len(candidates) == 1
    assert candidates[0].payment_type is None
    assert candidates[0].event_amount == 0
    assert candidates[0].total_saving == 4830
