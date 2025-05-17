import logging
from typing import List

from pydantic import ValidationError

from .categorization_serivce import CategorizationService
from .notification_service import NotificationService
from .user_service import UserService
from ..repositories.transaction_reposetory import TransactionRepository
from ..schemas.common import ImportSummary
from ..schemas.transaction import TransactionImport

logger = logging.getLogger(__name__)


class TransactionService:
    def __init__(
            self,
            tx_repo: TransactionRepository,
            user_service: UserService,
            categorization_service: CategorizationService,
            notification_service: NotificationService
    ):
        self.tx_repo = tx_repo
        self.user_service = user_service
        self.categorization_service = categorization_service
        self.notification_service = notification_service

    async def import_transactions(self, transactions_data: List[dict]) -> ImportSummary:
        imported_count = 0
        failed_imports = []

        logger.info(f"Начало импорта {len(transactions_data)} транзакций.")

        for i, tx_data in enumerate(transactions_data):
            try:
                transaction_schema = TransactionImport(**tx_data)

                if await self.tx_repo.get_by_id(transaction_schema.id):
                    logger.warning(f"Дубликат: {transaction_schema.id}")
                    failed_imports.append({"id": transaction_schema.id, "error": "Дубликат транзакции"})
                    continue

                db_user = await self.user_service.get_or_create(user_id=transaction_schema.user_id)

                category = self.categorization_service.categorize_transaction(transaction_schema.description)

                created_tx = await self.tx_repo.create(
                    obj_in=transaction_schema,
                    category=category
                )

                await self.notification_service.check_spending_limits(
                    db=self.tx_repo.db,
                    user_id=db_user.id,
                    transaction_timestamp=created_tx.timestamp
                )

                imported_count += 1

            except ValidationError as e:
                logger.error(f"Ошибка валидации: {e.errors()}")
                failed_imports.append({"id": tx_data.get("id"), "error": e.errors()})
            except Exception as e:
                logger.exception(f"Неизвестная ошибка: {str(e)}")
                failed_imports.append({"id": tx_data.get("id"), "error": str(e)})

        return ImportSummary(
            message="Транзакции частично или полностью импортированы.",
            imported_count=imported_count,
            failed_imports=failed_imports
        )
