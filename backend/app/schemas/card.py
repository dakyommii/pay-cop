from pydantic import BaseModel, ConfigDict, Field


class CardCreate(BaseModel):
    card_name: str = Field(min_length=1, max_length=100)
    card_type: str = Field(min_length=1, max_length=50)
    current_performance: float = Field(default=0, ge=0)
    required_performance: float = Field(default=0, ge=0)


class CardPerformanceUpdate(BaseModel):
    current_performance: float = Field(ge=0)


class CardRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    card_name: str
    card_type: str
    current_performance: float
    required_performance: float
