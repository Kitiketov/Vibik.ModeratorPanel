from __future__ import annotations

import ssl
from typing import Any, Optional

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from src.common.models.moderation_task import ModerationTask
from src.config import settings





# ---- client ----

class ModerationClient:
    def __init__(self, base_url: str, session: ClientSession, token: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.session = session
        self.headers: dict[str, str] = {}
        if settings.bot_secret:
            self.headers["Authorization"] = f"Bearer {settings.bot_secret}"



    async def next(self) -> ModerationTask | None:
        """
        GET /api/moderation/next
        200 -> JSON объекта
        204 -> пусто (нет задач)
        """
        url = f"{self.base_url}/api/moderation/next"
        timeout = ClientTimeout(total=10)
        async with self.session.get(url, headers=self.headers, timeout=timeout) as resp:
            if resp.status == 204:
                return None
            resp.raise_for_status()
            data: Any = await resp.json()
            return ModerationTask.model_validate(data)

    async def approve(self, user_task_id: int) -> bool:
        """
        POST /api/moderation/{id}/approve
        200 -> успешно одобрено
        """
        url = f"{self.base_url}/api/moderation/{user_task_id}/approve"
        timeout = ClientTimeout(total=10)
        async with self.session.post(url, headers=self.headers, timeout=timeout) as resp:
            resp.raise_for_status()
            return resp.status == 200

    async def reject(self, user_task_id: int) -> bool:
        """
        POST /api/moderation/{id}/reject
        200 -> успешно отклонено
        """
        url = f"{self.base_url}/api/moderation/{user_task_id}/reject"
        timeout = ClientTimeout(total=10)
        async with self.session.post(url, headers=self.headers, timeout=timeout) as resp:
            resp.raise_for_status()
            return resp.status == 200

    async def check_moderator(self, user_id: int) -> bool:
        """
        GET /api/moderation/{user_id}/check
        200 -> модератор авторизован (ожидаем bool/JSON)
        404/204 -> модератор не найден
        """
        url = f"{self.base_url}/api/moderation/{user_id}/check"
        timeout = ClientTimeout(total=10)
        async with self.session.get(url, headers=self.headers, timeout=timeout) as resp:
            if resp.status in (204, 404):
                return False
            resp.raise_for_status()
            data: Any = await resp.json()
            # если API вернёт {"authorized": true} — подстроимся:
            if isinstance(data, dict):
                # пробуем вытащить первое булево поле
                for v in data.values():
                    if isinstance(v, bool):
                        return v
            if isinstance(data, bool):
                return data
            return False


async def create_http_session() -> ClientSession:
    connector = aiohttp.TCPConnector()
    return aiohttp.ClientSession(connector=connector)
