from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.payment_event import PaymentEvent


def create_payment_event(
    db: Session, payment_type: str, merchant: str, benefit_rate: float
) -> PaymentEvent:
    event = PaymentEvent(payment_type=payment_type, merchant=merchant, benefit_rate=benefit_rate)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def list_events_for_merchant(db: Session, merchant: str) -> list[PaymentEvent]:
    stmt = select(PaymentEvent).where(PaymentEvent.merchant == merchant)
    return list(db.scalars(stmt))
