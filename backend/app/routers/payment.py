from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.payment import RecommendRequest, RecommendResponse
from app.services.payment_service import recommend_payment

router = APIRouter(prefix="/payment", tags=["payment"])


@router.post("/recommend", response_model=RecommendResponse)
def recommend(payload: RecommendRequest, db: Session = Depends(get_db)):
    return recommend_payment(
        db,
        merchant=payload.merchant,
        category=payload.category,
        amount=payload.amount,
        cards=payload.cards,
        payments=payload.payments,
    )
