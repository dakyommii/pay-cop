from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class PaymentEvent(Base):
    __tablename__ = "payment_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    payment_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    merchant: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    benefit_rate: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
