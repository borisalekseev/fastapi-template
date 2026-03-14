import logging
import os
from dataclasses import dataclass, field
from typing import Self

logger = logging.getLogger(__name__)


@dataclass(kw_only=True, slots=True, frozen=True)
class Config:
    asyncpg_dsn: str = field(repr=False)
    environment: str = "dev"

    def __post_init__(self) -> None:
        if self.environment not in {"dev", "prod"}:
            logger.warning("Unknown environment set: %s", self.environment)

    @classmethod
    def from_env(cls) -> Self:
        return cls(
            asyncpg_dsn=os.getenv(
                "ASYNCPG_DSN",
                "postgresql+asyncpg://app:app@localhost:5432/app",
            ),
            environment=os.getenv("ENVIRONMENT", "dev"),
        )
