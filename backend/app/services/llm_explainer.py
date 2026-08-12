"""Recommendation-reason generation (DESIGN.md §6.4, §6.6, §8).

The LLM never computes discounts or looks up benefits/events - it only turns
an already-computed Candidate into a user-friendly Korean explanation. If the
LLM call fails (no API key, network error, empty response, ...) a rule-based
fallback string is returned instead so the recommendation flow never breaks.
"""
from __future__ import annotations

from openai import OpenAI

from app.core.config import settings
from app.services.rule_engine import Candidate

SYSTEM_PROMPT = (
    "너는 이미 계산이 끝난 카드/간편결제 추천 결과를 사용자에게 설명하는 어시스턴트야. "
    "할인율이나 절약 금액을 새로 계산하거나 추측하지 말고, 주어진 수치만 사용해서 "
    "친근한 한국어 문장 2~3개로 추천 이유를 설명해. 대안이 주어지면 간단히 비교해줘. "
    "추천 조합의 총 예상 절약이 0원이면, 마치 유리한 카드가 있는 것처럼 포장하지 말고 "
    "'이번 결제에는 등록된 카드·간편결제로 받을 수 있는 혜택이 없다'는 사실을 있는 그대로 말해줘."
)


def _format_candidate(candidate: Candidate) -> str:
    return (
        f"카드: {candidate.card_name}, 간편결제: {candidate.payment_type or '없음'}, "
        f"카드 할인: {candidate.discount_amount}원({candidate.benefit_rate * 100:.0f}%, "
        f"업종 매칭: {candidate.benefit_category or '없음'}, 실적 조건 충족: {candidate.performance_met}), "
        f"간편결제 적립: {candidate.event_amount}원({candidate.event_rate * 100:.0f}%), "
        f"총 예상 절약: {candidate.total_saving}원"
    )


def _build_user_prompt(
    merchant: str,
    category: str,
    amount: float,
    top: Candidate,
    alternatives: list[Candidate],
) -> str:
    lines = [
        f"결제 매장: {merchant} (업종: {category}), 결제 금액: {amount}원",
        f"추천 조합: {_format_candidate(top)}",
    ]
    if alternatives:
        lines.append("다른 후보:")
        lines.extend(f"- {_format_candidate(c)}" for c in alternatives)
    return "\n".join(lines)


def _call_llm(user_prompt: str) -> str:
    client = OpenAI(api_key=settings.openai_api_key, timeout=10)
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    content = response.choices[0].message.content
    if not content or not content.strip():
        raise ValueError("LLM returned an empty response")
    return content.strip()


def _fallback_reason(merchant: str, top: Candidate) -> str:
    if top.total_saving <= 0:
        sentences = [f"이번 {merchant} 결제에는 등록된 카드나 간편결제로 받을 수 있는 혜택이 없습니다."]
        if top.benefit_category and not top.performance_met:
            sentences.append(f"{top.card_name}에 {merchant} 업종 할인이 있지만 이번 달 실적 조건을 채우지 못해 적용되지 않았습니다.")
        return " ".join(sentences)

    sentences = [f"현재 결제에서는 {top.card_name}가 가장 유리합니다."]

    if top.discount_amount > 0:
        rate_pct = round(top.benefit_rate * 100)
        sentences.append(f"{merchant} 업종 할인 {rate_pct}%가 적용되며 이번 달 실적 조건도 충족합니다.")
    elif top.benefit_category and not top.performance_met:
        sentences.append(f"{merchant} 업종 할인이 있지만 이번 달 실적 조건을 채우지 못해 적용되지 않았습니다.")

    if top.payment_type and top.event_amount > 0:
        rate_pct = round(top.event_rate * 100)
        sentences.append(f"추가로 {top.payment_type}를 함께 사용하면 {rate_pct}% 적립을 받을 수 있습니다.")

    return " ".join(sentences)


def generate_recommendation_reason(
    merchant: str,
    category: str,
    amount: float,
    top: Candidate,
    alternatives: list[Candidate] | None = None,
) -> str:
    alternatives = alternatives or []

    if not settings.openai_api_key:
        return _fallback_reason(merchant, top)

    try:
        prompt = _build_user_prompt(merchant, category, amount, top, alternatives)
        return _call_llm(prompt)
    except Exception:
        return _fallback_reason(merchant, top)
