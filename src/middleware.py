from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from src.api.photo_client import ModerationClient, create_http_session
from src.config import settings

class ModerationClientMiddleware(BaseMiddleware):
    def __init__(self):
        self.client: ModerationClient | None = None

    async def __call__(self, handler, event: TelegramObject, data: dict):
        if self.client is None:
            session = await create_http_session()
            self.client = ModerationClient(
                base_url=str(settings.API_BASE),
                session=session,
                token=settings.API_TOKEN,
            )
        
        data["moderation_client"] = self.client
        return await handler(event, data)
