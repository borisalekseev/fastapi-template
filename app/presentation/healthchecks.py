import sqlalchemy as sa
from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/check", route_class=DishkaRoute)


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readiness")
async def readiness_check(
    session: FromDishka[AsyncSession],
) -> dict[str, str]:
    try:
        await session.execute(sa.text("SELECT 1"))
    except SQLAlchemyError as e:
        return {"status": "error", "error": str(e)}
    return {"status": "ok"}
