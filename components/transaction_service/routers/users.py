import logging
import re
from datetime import date

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, Query
from starlette import status

from components.transaction_service.schemas.common import Msg
from components.transaction_service.schemas.user import UserStats
from components.transaction_service.services.statistics_service import StatisticsService

logger = logging.getLogger(__name__)

router = APIRouter(route_class=DishkaRoute)


async def validate_date_format(date_str: str) -> date:
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
        logger.error(f"Неверный формат даты: {date_str}. Ожидается YYYY-MM-DD.")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Неверный формат даты: '{date_str}'. Ожидается YYYY-MM-DD.",
        )
    try:
        return date.fromisoformat(date_str)
    except ValueError:
        logger.error(f"Некорректная дата: {date_str}.")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Некорректная дата: '{date_str}'.",
        )


@router.get(
    "/{user_id}/stats",
    response_model=UserStats,
    summary="Получение статистики по транзакциям пользователя",
    description="Возвращает общую сумму трат, траты по категориям и среднедневные траты "
                "для указанного пользователя за заданный период.",
    responses={
        404: {"description": "Пользователь не найден", "model": Msg},
        422: {"description": "Ошибка валидации параметров запроса"},
    }
)
async def get_user_stats_endpoint(
        statistics_service: FromDishka[StatisticsService],
        user_id: int,
        from_date_str: str = Query(..., alias="from", description="Начальная дата периода (YYYY-MM-DD)"),
        to_date_str: str = Query(..., alias="to", description="Конечная дата периода (YYYY-MM-DD)"),
):
    from_date = await validate_date_format(from_date_str)
    to_date = await validate_date_format(to_date_str)

    stats = await statistics_service.get_user_statistics(user_id, from_date, to_date)

    if not stats:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return stats
