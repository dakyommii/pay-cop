from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import CardNotFoundError
from app.models.card import Card
from app.repositories.card_repository import create_card, get_card, list_cards_for_user
from app.repositories.card_repository import update_performance as repo_update_performance
from app.services.user_service import get_user_or_404


def register_card(
    db: Session,
    user_id: int,
    card_name: str,
    card_type: str,
    current_performance: float,
    required_performance: float,
) -> Card:
    get_user_or_404(db, user_id)
    return create_card(
        db,
        user_id=user_id,
        card_name=card_name,
        card_type=card_type,
        current_performance=current_performance,
        required_performance=required_performance,
    )


def list_cards(db: Session, user_id: int) -> list[Card]:
    get_user_or_404(db, user_id)
    return list_cards_for_user(db, user_id)


def update_card_performance(
    db: Session, user_id: int, card_id: int, current_performance: float
) -> Card:
    get_user_or_404(db, user_id)
    card = get_card(db, card_id)
    if card is None or card.user_id != user_id:
        raise CardNotFoundError(f"Card {card_id} not found for user {user_id}")
    return repo_update_performance(db, card, current_performance=current_performance)
