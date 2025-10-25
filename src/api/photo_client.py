# src/api/moderation_client.py
from __future__ import annotations
import ssl
import aiohttp
from typing import Any
from pydantic import BaseModel, HttpUrl
from aiohttp import ClientSession, ClientTimeout
from src.config import settings


class ModerationItem(BaseModel):
    id: int
    url: HttpUrl
    author: str | None = None
    theme: str | None = None
    tags: list[str] = []
    description: str | None = None


def _build_ssl(verify: bool, ca_path: str | None) -> ssl.SSLContext | bool:
    if not verify:
        return False                     # отключаем проверку в DEV (только локально!)
    if ca_path:
        ctx = ssl.create_default_context(cafile=ca_path)
        return ctx
    return ssl.create_default_context()   # обычная проверка


class ModerationClient:
    def __init__(self, base_url: str, session: ClientSession, token: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.session = session
        self.headers = {"Authorization": f"Bearer {token}"} if token else None

    async def next(self) -> ModerationItem | None:
        """
        GET /api/moderation/next
        200 -> JSON объекта
        204 -> пусто (нет задач)
        """
        url = f"{self.base_url}/api/moderation/next"
        timeout = ClientTimeout(total=10)
        print(2)
        async with self.session.get(url, timeout=timeout) as resp:
            if resp.status == 204:
                return None
            print(1)
            resp.raise_for_status()
            data: Any = await resp.json()
            return ModerationItem.model_validate(data)

    async def approve(self, item_id: int) -> bool:
        """
        POST /api/moderation/{id}/approve
        200 -> успешно одобрено
        """
        url = f"{self.base_url}/api/moderation/{item_id}/approve"
        timeout = ClientTimeout(total=10)
        async with self.session.post(url, headers=self.headers, timeout=timeout) as resp:
            resp.raise_for_status()
            return resp.status == 200

    async def reject(self, item_id: int) -> bool:
        """
        POST /api/moderation/{id}/reject
        200 -> успешно отклонено
        """
        url = f"{self.base_url}/api/moderation/{item_id}/reject"
        timeout = ClientTimeout(total=10)
        async with self.session.post(url, headers=self.headers, timeout=timeout) as resp:
            resp.raise_for_status()
            return resp.status == 200

    async def check_moderator(self, user_id: int) -> bool:
        """
        GET /api/moderators/{user_id}/check
        200 -> модератор авторизован
        404 -> модератор не найден
        """
        url = f"{self.base_url}/api/moderation/{user_id}/check"
        timeout = ClientTimeout(total=10)
        async with self.session.get(url, headers=self.headers, timeout=timeout) as resp:
            if resp.status == 404:
                return False
            resp.raise_for_status()
            return resp.status == 200


async def create_http_session() -> ClientSession:
    ssl_ctx_or_flag = _build_ssl(settings.VERIFY_SSL, settings.CA_CERT_PATH)
    connector = aiohttp.TCPConnector(ssl=ssl_ctx_or_flag)
    return aiohttp.ClientSession(connector=connector)
