from __future__ import annotations

from sqlalchemy.orm import Session

from app.schemas.payment import CandidateItem, CardPerformanceInput, RecommendResponse
from app.services.llm_explainer import generate_recommendation_reason
from app.services.rule_engine import CardInput, build_candidates


def recommend_payment(
    db: Session,
    merchant: str,
    category: str,
    amount: float,
    cards: list[CardPerformanceInput],
    payments: list[str],
) -> RecommendResponse:
    card_inputs = [
        CardInput(name=c.name, performance=c.performance, required_performance=c.required_performance)
        for c in cards
    ]
    candidates = build_candidates(
        db, merchant=merchant, category=category, amount=amount, cards=card_inputs, payments=payments
    )

    top = candidates[0]
    alternatives = candidates[1:4]
    reason = generate_recommendation_reason(merchant, category, amount, top, alternatives)

    candidate_items = [
        CandidateItem(
            card_name=c.card_name,
            payment_type=c.payment_type,
            expected_saving=c.total_saving,
            performance_met=c.performance_met,
        )
        for c in candidates[:5]
    ]

    return RecommendResponse(
        recommended_card=top.card_name,
        recommended_payment=top.payment_type,
        expected_saving=top.total_saving,
        reason=reason,
        candidates=candidate_items,
    )
