from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.benefit import Benefit


def create_benefit(
    db: Session, card_name: str, category: str, discount_rate: float, condition: str | None = None
) -> Benefit:
    benefit = Benefit(
        card_name=card_name, category=category, discount_rate=discount_rate, condition=condition
    )
    db.add(benefit)
    db.commit()
    db.refresh(benefit)
    return benefit


def list_benefits_for_card(db: Session, card_name: str) -> list[Benefit]:
    stmt = select(Benefit).where(Benefit.card_name == card_name)
    return list(db.scalars(stmt))
