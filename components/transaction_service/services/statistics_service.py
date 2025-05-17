import logging
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from components.transaction_service.config import Config
from components.transaction_service.repositories.transaction_reposetory import TransactionRepository
from components.transaction_service.repositories.user_reposetory import UserRepository
from components.transaction_service.schemas.user import UserStats

logger = logging.getLogger(__name__)


class StatisticsService:
    def __init__(
            self,
            cfg: Config,
            user_repo: UserRepository,
            transaction_repo: TransactionRepository,
    ):
        self.categories = cfg.categorization.categories
        self.default_category = cfg.categorization.default_category
        self.user_repo = user_repo
        self.transaction_repo = transaction_repo

    async def get_user_statistics(
            self,
            user_id: int,
            from_date: date,
            to_date: date
    ) -> UserStats | None:
        logger.info(f"Запрос статистики для user_id={user_id} за период {from_date} - {to_date}")

        db_user = await self.user_repo.get(user_id)
        if not db_user:
            logger.warning(f"Пользователь с ID {user_id} не найден для получения статистики.")
            return None

        total_spent = await self.transaction_repo.get_total_spent_for_user_period(
            user_id=user_id, start_date=from_date, end_date=to_date
        )

        logger.debug(f"Общая сумма трат для user_id={user_id}: {total_spent}")

        by_category = {category: Decimal("0.00") for category in self.categories}
        spending_by_cat_db = await self.transaction_repo.get_spending_by_category(
            user_id=user_id, start_date=from_date, end_date=to_date
        )
        logger.debug(f"Траты по категориям из БД: {spending_by_cat_db}")

        for category, amount in spending_by_cat_db.items():
            if category in by_category:
                by_category[category] = amount
            elif self.default_category in by_category:
                by_category[self.default_category] += amount
                logger.warning(
                    f"Неизвестная категория '{category}' ({amount}) отнесена к '{self.default_category}'."
                )
            else:
                logger.warning(f"Неизвестная категория '{category}' не может быть отнесена к 'Other'.")

        daily_average_spent = None
        if total_spent > 0:
            num_days = (to_date - from_date).days + 1
            if num_days > 0:
                daily_average_spent = (total_spent / Decimal(num_days)).quantize(Decimal("0.01"),
                                                                                 rounding=ROUND_HALF_UP)

        stats_data = UserStats(
            user_id=user_id,
            from_date=from_date.isoformat(),
            to_date=to_date.isoformat(),
            total_spent=total_spent,
            by_category=by_category,
            daily_average_spent=daily_average_spent,
        )
        logger.info(f"Статистика для user_id={user_id} успешно сформирована.")
        return stats_data
