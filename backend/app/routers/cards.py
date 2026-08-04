from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.card import CardCreate, CardPerformanceUpdate, CardRead
from app.services.card_service import list_cards, register_card, update_card_performance

router = APIRouter(prefix="/users/{user_id}/cards", tags=["cards"])


@router.post("", response_model=CardRead, status_code=201)
def create_card_endpoint(user_id: int, payload: CardCreate, db: Session = Depends(get_db)):
    return register_card(
        db,
        user_id=user_id,
        card_name=payload.card_name,
        card_type=payload.card_type,
        current_performance=payload.current_performance,
        required_performance=payload.required_performance,
    )


@router.get("", response_model=list[CardRead])
def list_cards_endpoint(user_id: int, db: Session = Depends(get_db)):
    return list_cards(db, user_id)


@router.patch("/{card_id}/performance", response_model=CardRead)
def update_card_performance_endpoint(
    user_id: int, card_id: int, payload: CardPerformanceUpdate, db: Session = Depends(get_db)
):
    return update_card_performance(
        db, user_id=user_id, card_id=card_id, current_performance=payload.current_performance
    )
