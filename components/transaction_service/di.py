import os
from collections.abc import AsyncGenerator

from dishka import Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    async_sessionmaker, create_async_engine)

from components.transaction_service.config import Config, load_config
from components.transaction_service.models import Base
from components.transaction_service.repositories.transaction_reposetory import TransactionRepository
from components.transaction_service.repositories.user_reposetory import UserRepository
from components.transaction_service.services.categorization_serivce import CategorizationService
from components.transaction_service.services.notification_service import NotificationService
from components.transaction_service.services.statistics_service import StatisticsService
from components.transaction_service.services.transaction_service import TransactionService
from components.transaction_service.services.user_service import UserService


def config_provider() -> Provider:
    provider = Provider()

    cfg_path = os.getenv('TRANSACTION_SERVICE_CONFIG_PATH',
                         './components/transaction_service/configs/app.toml')
    provider.provide(lambda: load_config(cfg_path),
                     scope=Scope.APP, provides=Config)
    return provider


class TransactionServiceProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_engine(self, cfg: Config) -> AsyncEngine:
        return create_async_engine(cfg.db.uri, echo=False)

    @provide(scope=Scope.APP)
    async def get_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_session(
            self,
            sessionmaker: async_sessionmaker
    ) -> AsyncGenerator[AsyncSession, None, None]:
        async with sessionmaker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    async def get_transaction_repository(self, session: AsyncSession) -> TransactionRepository:
        return TransactionRepository(db=session)

    @provide(scope=Scope.APP)
    def get_categorization_service(self, cfg: Config) -> CategorizationService:
        return CategorizationService(cfg)

    @provide(scope=Scope.APP)
    def get_notification_service(self, cfg: Config) -> NotificationService:
        return NotificationService(cfg)

    @provide(scope=Scope.REQUEST)
    def get_statistics_service(self, cfg: Config, user_repo: UserRepository,
                               transaction_repo: TransactionRepository) -> StatisticsService:
        return StatisticsService(cfg, user_repo, transaction_repo)

    @provide(scope=Scope.REQUEST)
    async def get_transaction_service(
            self,
            tx_repo: TransactionRepository,
            user_service: UserService,
            categorization_service: CategorizationService,
            notification_service: NotificationService
    ) -> TransactionService:
        return TransactionService(
            tx_repo=tx_repo,
            user_service=user_service,
            categorization_service=categorization_service,
            notification_service=notification_service
        )

    @provide(scope=Scope.REQUEST)
    async def get_user_repository(self, session: AsyncSession) -> UserRepository:
        return UserRepository(session)

    @provide(scope=Scope.REQUEST)
    async def get_user_service(self, user_repo: UserRepository) -> UserService:
        return UserService(repo=user_repo)


def setup_di():
    return make_async_container(
        config_provider(),
        TransactionServiceProvider(),
    )
