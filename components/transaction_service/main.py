from contextlib import asynccontextmanager
from typing import AsyncGenerator

from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator

from components.transaction_service.di import setup_di
from components.transaction_service.routers.transaction import router as transaction_router
from components.transaction_service.routers.users import router as users_router
from shared.logging_config import setup_logging

SERVICE_NAME = "transaction-service"
setup_logging(SERVICE_NAME)


@asynccontextmanager
async def lifespan(app_: FastAPI) -> AsyncGenerator[None, None]:
    yield

    await app_.container.close()


def create_app(ioc_container: AsyncContainer):
    application = FastAPI(title="Transaction Service",
                          version="1.0.0", lifespan=lifespan)

    instrumentator = Instrumentator(
        should_group_status_codes=False,
        excluded_handlers=['/health'],
    )

    instrumentator.instrument(application)

    setup_dishka(container=ioc_container, app=application)
    application.container = ioc_container

    application.include_router(transaction_router, prefix="/transactions", tags=["Transactions"])
    application.include_router(users_router, prefix="/users", tags=["Users & Statistics"])

    instrumentator.expose(application, include_in_schema=False, should_gzip=True)

    @application.get("/health")
    async def health_check():
        logger.debug("Health check endpoint called")
        return {"status": "healthy"}

    logger.info("FastAPI application created and configured.")
    return application


logger.info("Setting up DI container...")
container = setup_di()

logger.info("Creating FastAPI application...")
app = create_app(container)

logger.info(f"{SERVICE_NAME} application ready.")
