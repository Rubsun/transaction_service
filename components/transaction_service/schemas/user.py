from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Dict, Optional
from decimal import Decimal

class UserBase(BaseModel):
    pass

class User(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserStats(BaseModel):
    user_id: int
    from_date: str
    to_date: str
    total_spent: Decimal
    by_category: Dict[str, Decimal]
    daily_average_spent: Optional[Decimal] = None

    model_config = ConfigDict(
        json_encoders={
            Decimal: lambda v: float(round(v, 2))
        }
    )

