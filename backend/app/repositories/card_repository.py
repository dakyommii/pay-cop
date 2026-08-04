from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.card import Card


def create_card(
    db: Session,
    user_id: int,
    card_name: str,
    card_type: str,
    current_performance: float,
    required_performance: float,
) -> Card:
    card = Card(
        user_id=user_id,
        card_name=card_name,
        card_type=card_type,
        current_performance=current_performance,
        required_performance=required_performance,
    )
    db.add(card)
    db.commit()
    db.refresh(card)
    return card


def get_card(db: Session, card_id: int) -> Card | None:
    return db.get(Card, card_id)


def list_cards_for_user(db: Session, user_id: int) -> list[Card]:
    stmt = select(Card).where(Card.user_id == user_id)
    return list(db.scalars(stmt))


def update_performance(db: Session, card: Card, current_performance: float) -> Card:
    card.current_performance = current_performance
    db.commit()
    db.refresh(card)
    return card
