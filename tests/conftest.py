import threading
from collections.abc import AsyncGenerator
from unittest import mock

import alembic.command
import alembic.config
import dishka
import pytest
from dishka import provide
from dishka.integrations.fastapi import setup_dishka
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

from app.__main__ import create_app, create_container
from app.config import Config


@pytest.fixture(scope="session")
def test_config() -> Config:
    return Config(
        asyncpg_dsn="postgresql+asyncpg://app:app@localhost:5432/app",
    )


@pytest.fixture(scope="session")
async def test_engine(test_config: Config) -> AsyncGenerator[AsyncEngine]:
    engine = create_async_engine(
        test_config.asyncpg_dsn,
        future=True,
    )

    migrations_exc: BaseException | None = None

    def run_migrations() -> None:
        nonlocal migrations_exc
        try:
            alembic_cfg = alembic.config.Config("alembic.ini")
            alembic.command.upgrade(alembic_cfg, "head")
        except BaseException as exc:  # noqa: BLE001
            migrations_exc = exc
            raise

    thread = threading.Thread(target=run_migrations)
    thread.start()
    thread.join()

    if migrations_exc:
        raise migrations_exc

    yield engine

    await engine.dispose()


@pytest.fixture
def commit_mock() -> mock.AsyncMock:
    return mock.AsyncMock()


@pytest.fixture
async def test_session(
    test_engine: AsyncEngine, commit_mock: mock.AsyncMock
) -> AsyncGenerator[AsyncSession]:
    async with (
        AsyncSession(test_engine, expire_on_commit=False) as session,
        session.begin(),
    ):
        session.commit = commit_mock  # type: ignore[method-assign]
        yield session
        await session.rollback()


@pytest.fixture
def test_dishka_provider(test_session: AsyncSession) -> dishka.Provider:
    class TestDishkaProvider(dishka.Provider):
        override = True

        @provide(scope=dishka.Scope.REQUEST)
        def session(self) -> AsyncSession:
            return test_session

    return TestDishkaProvider()


@pytest.fixture
async def test_client(
    test_config: Config,
    test_dishka_provider: dishka.Provider,
) -> AsyncGenerator[AsyncClient]:
    app = create_app(test_config)
    container = create_container(test_config, test_dishka_provider)
    setup_dishka(container, app)
    async with (
        AsyncClient(
            base_url="http://test",
            transport=ASGITransport(app),
        ) as client,
    ):
        yield client
