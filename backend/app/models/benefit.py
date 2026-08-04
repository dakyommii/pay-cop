from sqlalchemy import Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Benefit(Base):
    """Card benefit catalog entry.

    Keyed by card_name (not a FK to a specific user's Card row) because a
    benefit belongs to a card product (e.g. "신한카드"), shared across every
    user who registers that card - not to one user's registration instance.
    """

    __tablename__ = "benefits"

    id: Mapped[int] = mapped_column(primary_key=True)
    card_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    discount_rate: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    condition: Mapped[str] = mapped_column(String(200), nullable=True)
