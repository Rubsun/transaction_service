from pydantic import BaseModel, ConfigDict, field_validator, Field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal # Используем Decimal для точности денежных сумм

class TransactionBase(BaseModel):
    id: str = Field(..., description="Уникальный идентификатор транзакции")
    user_id: int = Field(..., description="ID пользователя")
    amount: Decimal = Field(..., description="Сумма транзакции (отрицательная для расходов)")
    currency: str = Field(..., min_length=3, max_length=3, description="Код валюты (например, RUB)")
    description: Optional[str] = Field(None, description="Описание транзакции (для категоризации)")
    timestamp: datetime = Field(..., description="Дата и время транзакции")

    @field_validator('amount')
    def amount_must_be_valid_decimal(cls, value):
        if not isinstance(value, Decimal):
            try:
                return Decimal(str(value))
            except Exception:
                raise ValueError("Amount must be a valid number")
        return value

class TransactionCreate(TransactionBase):
    pass

class TransactionImport(TransactionCreate):
    pass


class Transaction(TransactionBase):
    category: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TransactionImportRequest(BaseModel):
    transactions: List[TransactionImport]

