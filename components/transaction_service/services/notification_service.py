import logging
from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from components.transaction_service.config import Config
from components.transaction_service.repositories.transaction_reposetory import TransactionRepository

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, cfg: Config):
        self.daily_limit = Decimal(str(cfg.limits.daily_spending_limit))
        self.weekly_limit = Decimal(str(cfg.limits.weekly_spending_limit))
        self.default_currency = "RUB"

        logger.info(
            f"Сервис уведомлений инициализирован. "
            f"Дневной лимит: {self.daily_limit}, Недельный лимит: {self.weekly_limit}"
        )

    async def check_spending_limits(
            self,
            db: AsyncSession,
            user_id: int,
            transaction_timestamp: datetime
    ):
        repo = TransactionRepository(db)
        transaction_date = transaction_timestamp.date()

        daily_spent = await repo.get_total_spent_for_user_period(
            user_id=user_id, start_date=transaction_date, end_date=transaction_date
        )
        if daily_spent > self.daily_limit:
            logger.warning(
                f"ПРЕВЫШЕНИЕ ДНЕВНОГО ЛИМИТА! Пользователь ID {user_id} потратил {daily_spent:.2f} "
                f"{self.default_currency} за {transaction_date}. Лимит: {self.daily_limit:.2f}"
            )

        start_of_week = transaction_date - timedelta(days=transaction_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        weekly_spent = await repo.get_total_spent_for_user_period(
            user_id=user_id, start_date=start_of_week, end_date=end_of_week
        )
        if weekly_spent > self.weekly_limit:
            logger.warning(
                f"ПРЕВЫШЕНИЕ НЕДЕЛЬНОГО ЛИМИТА! Пользователь ID {user_id} потратил {weekly_spent:.2f} "
                f"{self.default_currency} за неделю {start_of_week} - {end_of_week}. Лимит: {self.weekly_limit:.2f}"
            )
