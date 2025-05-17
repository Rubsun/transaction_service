import logging
from typing import List

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, status, Body

from components.transaction_service.schemas.common import ImportSummary
from components.transaction_service.schemas.transaction import TransactionImport
from components.transaction_service.services.transaction_service import TransactionService

logger = logging.getLogger(__name__)

router = APIRouter(route_class=DishkaRoute)


@router.post(
    "/import",
    response_model=ImportSummary,
    status_code=status.HTTP_201_CREATED,
    summary="Импорт списка транзакций",
    description="Загружает список транзакций, валидирует, категоризирует и сохраняет их. "
                "Проверяет на дубликаты по ID транзакции.",
)
async def import_transactions_endpoint(
        transaction_service: FromDishka[TransactionService],
        transactions_in: List[TransactionImport] = Body(..., embed=False, description="Список транзакций для импорта"),
) -> ImportSummary:
    logger.info(f"Получен запрос на импорт {len(transactions_in)} транзакций.")
    transactions_data = [tx.model_dump() for tx in transactions_in]
    return await transaction_service.import_transactions(transactions_data)
