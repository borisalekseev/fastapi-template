import logging

import dishka
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.config import Config
from app.ioc import InfraProvider
from app.presentation import healthchecks
from app.presentation.exception_handlers import EXCEPTION_HANDLERS

logger = logging.getLogger(__name__)


def create_app(config: Config) -> FastAPI:
    is_prod = config.environment == "prod"
    app = FastAPI(
        title="app",
        openapi_url=None if is_prod else "/api/v1/openapi.json",
        docs_url=None if is_prod else "/docs",
        redoc_url=None if is_prod else "/redoc",
        exception_handlers=EXCEPTION_HANDLERS,
    )

    app.include_router(healthchecks.router)

    return app


def create_container(
    config: Config,
    *additional_providers: dishka.Provider,
) -> dishka.AsyncContainer:
    return dishka.make_async_container(
        InfraProvider(),
        *additional_providers,
        context={
            Config: config,
        },
    )


def get_app() -> FastAPI:
    config = Config.from_env()
    container = create_container(config)
    app = create_app(config)
    setup_dishka(container, app)
    return app
