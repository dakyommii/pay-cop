"""Pure calculation engine for payment recommendations (DESIGN.md §9).

No LLM involved here - this module only looks up benefits/events and computes
expected savings. LLM-based explanation generation is a separate concern
(DESIGN.md §8) added in a later step.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.repositories.benefit_repository import list_benefits_for_card
from app.repositories.payment_event_repository import list_events_for_merchant


@dataclass
class CardInput:
    name: str
    performance: float
    required_performance: float = 0.0


@dataclass
class Candidate:
    card_name: str
    payment_type: str | None
    performance_met: bool
    benefit_category: str | None
    benefit_rate: float
    discount_amount: float
    event_rate: float
    event_amount: float
    total_saving: float


def build_candidates(
    db: Session,
    merchant: str,
    category: str,
    amount: float,
    cards: list[CardInput],
    payments: list[str],
) -> list[Candidate]:
    payment_options: list[str | None] = list(payments) if payments else [None]
    candidates: list[Candidate] = []

    for card in cards:
        performance_met = card.performance >= card.required_performance

        benefits = list_benefits_for_card(db, card.name)
        matching_benefit = next(
            (b for b in benefits if b.category in (merchant, category)), None
        )

        if matching_benefit and performance_met:
            benefit_rate = float(matching_benefit.discount_rate)
            discount_amount = round(amount * benefit_rate)
        else:
            benefit_rate = 0.0
            discount_amount = 0

        benefit_category = matching_benefit.category if matching_benefit else None

        events = list_events_for_merchant(db, merchant)

        for payment in payment_options:
            matching_event = next((e for e in events if e.payment_type == payment), None)
            event_rate = float(matching_event.benefit_rate) if matching_event else 0.0
            event_amount = round(amount * event_rate)

            candidates.append(
                Candidate(
                    card_name=card.name,
                    payment_type=payment,
                    performance_met=performance_met,
                    benefit_category=benefit_category,
                    benefit_rate=benefit_rate,
                    discount_amount=discount_amount,
                    event_rate=event_rate,
                    event_amount=event_amount,
                    total_saving=discount_amount + event_amount,
                )
            )

    candidates.sort(key=lambda c: c.total_saving, reverse=True)
    return candidates
