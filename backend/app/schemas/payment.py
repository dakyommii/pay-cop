from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CardPerformanceInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1)
    performance: float = Field(ge=0)
    # Not part of DESIGN.md §11's example payload, but needed for the "실적 조건
    # 확인" step (§9). Defaults to 0 (no requirement) so the example request
    # still validates as-is; callers with a registered Card should pass the
    # card's required_performance here (wired up on the frontend side).
    required_performance: float = Field(default=0, ge=0, alias="requiredPerformance")


class RecommendRequest(BaseModel):
    merchant: str = Field(min_length=1)
    category: str = Field(min_length=1)
    amount: float = Field(gt=0)
    cards: list[CardPerformanceInput] = Field(min_length=1)
    payments: list[str] = Field(default_factory=list)


class CandidateItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    card_name: str = Field(alias="cardName")
    payment_type: Optional[str] = Field(alias="paymentType")
    expected_saving: float = Field(alias="expectedSaving")
    performance_met: bool = Field(alias="performanceMet")


class RecommendResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    recommended_card: str = Field(alias="recommendedCard")
    recommended_payment: Optional[str] = Field(alias="recommendedPayment")
    expected_saving: float = Field(alias="expectedSaving")
    reason: str
    # Additive extension beyond DESIGN.md §11's example (which only returns the
    # top pick): the "절약 금액 비교" screen (§13 ⑤) needs the other candidates
    # too. recommendedCard/recommendedPayment/expectedSaving/reason keep their
    # exact §11 shape; this is purely additive.
    candidates: list[CandidateItem] = Field(default_factory=list)
