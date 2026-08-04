"""Idempotent sample-data seeding for local/dev use (DESIGN.md §6.2, §6.3).

Run with: python -m scripts.seed   (from the backend/ directory, venv active)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import SessionLocal  # noqa: E402
from app.models.benefit import Benefit  # noqa: E402
from app.models.payment_event import PaymentEvent  # noqa: E402

BENEFITS = [
    ("신한카드", "편의점", 0.10, "실적 30만원 이상"),
    ("신한카드", "올리브영", 0.10, "실적 30만원 이상"),
    ("신한카드", "스타벅스", 0.20, "실적 30만원 이상"),
    ("삼성카드", "주유", 0.05, "실적 50만원 이상"),
    ("삼성카드", "온라인쇼핑", 0.10, "실적 50만원 이상"),
    ("현대카드", "영화", 0.15, "실적 40만원 이상"),
    ("현대카드", "배달앱", 0.10, "실적 40만원 이상"),
]

PAYMENT_EVENTS = [
    ("네이버페이", "올리브영", 0.02),
    ("카카오페이", "맥도날드", 0.05),
    ("토스페이", "편의점", 0.10),
]


def seed() -> None:
    db = SessionLocal()
    try:
        for card_name, category, discount_rate, condition in BENEFITS:
            exists = (
                db.query(Benefit)
                .filter_by(card_name=card_name, category=category)
                .first()
            )
            if exists:
                continue
            db.add(
                Benefit(
                    card_name=card_name,
                    category=category,
                    discount_rate=discount_rate,
                    condition=condition,
                )
            )

        for payment_type, merchant, benefit_rate in PAYMENT_EVENTS:
            exists = (
                db.query(PaymentEvent)
                .filter_by(payment_type=payment_type, merchant=merchant)
                .first()
            )
            if exists:
                continue
            db.add(
                PaymentEvent(
                    payment_type=payment_type, merchant=merchant, benefit_rate=benefit_rate
                )
            )

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
    print("Seed complete.")
