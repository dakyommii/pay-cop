from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    card_name: Mapped[str] = mapped_column(String(100), nullable=False)
    card_type: Mapped[str] = mapped_column(String(50), nullable=False)
    current_performance: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    required_performance: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0)

    user: Mapped["User"] = relationship(back_populates="cards")
