from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.moderation.client import ModerationClient


class ModerationClientMiddleware(BaseMiddleware):
    def __init__(self, client: ModerationClient):
        self.client = client

    async def __call__(self, handler, event: TelegramObject, data: dict):
        data["moderation_client"] = self.client
        return await handler(event, data)
