from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import Optional


from components.transaction_service.models import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db


    async def get(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user_id: int) -> User:
        user = User(id=user_id)
        self.db.add(user)
        try:
            await self.db.commit()
            await self.db.refresh(user)
            logger.info(f"Пользователь с ID {user_id} успешно создан.")
            return user
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Ошибка при создании пользователя с ID {user_id}: {e}")
            raise
