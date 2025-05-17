import logging

from components.transaction_service.models import User
from components.transaction_service.repositories.user_reposetory import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_or_create(self, user_id: int) -> User:
        user = await self.repo.get(user_id)
        if user:
            logger.debug(f"Пользователь с ID {user_id} найден.")
            return user

        logger.info(f"Пользователь с ID {user_id} не найден, создаем нового.")
        return await self.repo.create(user_id)
