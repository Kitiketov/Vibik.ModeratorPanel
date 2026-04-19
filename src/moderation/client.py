from __future__ import annotations

from typing import Any

import aiohttp
from aiohttp import ClientSession, ClientTimeout

from src.core.config import settings
from src.moderation.models import MetricsListModel, ModerationTask,ModeratorCheckResponse


class ModerationClient:
    def __init__(self, base_url: str, session: ClientSession):
        self.base_url = base_url.rstrip("/")
        self.session = session
        self.headers: dict[str, str] = {}
        if settings.bot_secret:
            self.headers["Authorization"] = f"Bearer {settings.bot_secret}"

    async def next(self) -> ModerationTask | None:
        url = f"{self.base_url}/api/moderation/next"
        timeout = ClientTimeout(total=10)
        async with self.session.get(url, headers=self.headers, timeout=timeout) as resp:
            if resp.status == 204:
                return None
            resp.raise_for_status()
            data: Any = await resp.json()
            return ModerationTask.model_validate(data)

    async def metrics(self) -> MetricsListModel | None:
        url = f"{self.base_url}/api/metrics"
        timeout = ClientTimeout(total=10)
        async with self.session.get(url, headers=self.headers, timeout=timeout) as resp:
            if resp.status == 204:
                return None
            resp.raise_for_status()
            data = await resp.json()
            return MetricsListModel.model_validate(data)

    async def approve(self, user_task_id: int) -> bool:
        url = f"{self.base_url}/api/moderation/{user_task_id}/approve"
        timeout = ClientTimeout(total=10)
        async with self.session.post(url, headers=self.headers, timeout=timeout) as resp:
            resp.raise_for_status()
            return resp.status == 200

    async def reject(self, user_task_id: int) -> bool:
        url = f"{self.base_url}/api/moderation/{user_task_id}/reject"
        timeout = ClientTimeout(total=10)
        async with self.session.post(url, headers=self.headers, timeout=timeout) as resp:
            resp.raise_for_status()
            return resp.status == 200

    async def check_moderator(self, user_id: int) -> bool:
        url = f"{self.base_url}/api/moderation/{user_id}/check"
        timeout = ClientTimeout(total=10)
        async with self.session.get(url, headers=self.headers, timeout=timeout) as resp:
            if resp.status in (204, 404):
                return False
            resp.raise_for_status()
            data = await resp.json()
            if isinstance(data, bool):
                return data
            return False

async def create_http_session() -> ClientSession:
    connector = aiohttp.TCPConnector()
    return aiohttp.ClientSession(connector=connector)
