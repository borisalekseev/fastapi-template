from http import HTTPStatus

from httpx import AsyncClient


async def test_health(test_client: AsyncClient) -> None:
    response = await test_client.get("/check/health")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}


async def test_readiness(test_client: AsyncClient) -> None:
    response = await test_client.get("/check/readiness")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"status": "ok"}
