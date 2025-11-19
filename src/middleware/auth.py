from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from src.api.photo_client import ModerationClient
from src.texts.auth_text import (
    no_rights,
    access_check_error,
    no_rights_alert,
    access_check_error_alert,
)


class ModeratorAuthMiddleware(BaseMiddleware):
    def __init__(self):
        self.client: ModerationClient | None = None

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        self.client = data.get("moderation_client")

        if not self.client:
            return await handler(event, data)


        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if not user_id:
            return await handler(event, data)

        try:
            is_moderator = await self.client.check_moderator(user_id)
            if not is_moderator:
                if isinstance(event, Message):
                    await event.answer(no_rights)
                elif isinstance(event, CallbackQuery):
                    await event.answer(no_rights_alert, show_alert=True)
                return
        except Exception as e:
            print(f"Error checking moderator auth: {e}")
            if isinstance(event, Message):
                await event.answer(access_check_error)
            elif isinstance(event, CallbackQuery):
                await event.answer(access_check_error_alert, show_alert=True)
            return

        return await handler(event, data)
