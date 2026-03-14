from collections.abc import AsyncGenerator

import dishka
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import Config


class InfraProvider(dishka.Provider):
    @dishka.provide(scope=dishka.Scope.APP)
    def session_factory(self, config: Config) -> async_sessionmaker[AsyncSession]:
        engine = create_async_engine(
            config.asyncpg_dsn,
            pool_size=5,
            max_overflow=96,
            pool_timeout=30,
        )
        return async_sessionmaker(engine)

    @dishka.provide(scope=dishka.Scope.REQUEST)
    async def session(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncGenerator[AsyncSession]:
        async with session_factory() as session:
            yield session
