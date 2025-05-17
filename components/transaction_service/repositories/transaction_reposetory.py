from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from components.transaction_service.models import Transaction
from components.transaction_service.schemas.transaction import TransactionCreate


class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, transaction_id: str) -> Optional[Transaction]:
        stmt = select(Transaction).where(Transaction.id == transaction_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, obj_in: TransactionCreate, category: str) -> Transaction:
        data = obj_in.model_dump()
        if 'amount' in data and not isinstance(data['amount'], Decimal):
            data['amount'] = Decimal(str(data['amount']))
        db_obj = Transaction(**data, category=category)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def get_for_user_period(self, user_id: int, start_date: date, end_date: date) -> List[Transaction]:
        start = datetime.combine(start_date, time.min)
        end = datetime.combine(end_date, time.max)
        stmt = (
            select(Transaction)
            .where(
                Transaction.user_id == user_id,
                Transaction.timestamp >= start,
                Transaction.timestamp <= end
            )
            .order_by(Transaction.timestamp)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_total_spent_for_user_period(self, user_id: int, start_date: date, end_date: date) -> Decimal:
        start = datetime.combine(start_date, time.min)
        end = datetime.combine(end_date, time.max)
        stmt = (
            select(func.sum(Transaction.amount))
            .where(
                Transaction.user_id == user_id,
                Transaction.amount < 0,
                Transaction.timestamp >= start,
                Transaction.timestamp <= end
            )
        )
        result = await self.db.execute(stmt)
        total = result.scalar()
        return Decimal(str(abs(total))) if total is not None else Decimal("0.00")

    async def get_spending_by_category(self, user_id: int, start_date: date, end_date: date) -> dict[str, Decimal]:
        start = datetime.combine(start_date, time.min)
        end = datetime.combine(end_date, time.max)
        stmt = (
            select(Transaction.category, func.sum(Transaction.amount).label("total"))
            .where(
                Transaction.user_id == user_id,
                Transaction.amount < 0,
                Transaction.timestamp >= start,
                Transaction.timestamp <= end
            )
            .group_by(Transaction.category)
        )
        result = await self.db.execute(stmt)
        rows = result.all()
        return {category: Decimal(str(abs(total))) for category, total in rows}
