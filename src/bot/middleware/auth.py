from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from src.bot.texts.auth_text import access_check_error, access_check_error_alert, no_rights, no_rights_alert
from src.moderation.client import ModerationClient


class ModeratorAuthMiddleware(BaseMiddleware):
    def __init__(self):
        self.client: ModerationClient | None = None

    async def __call__(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: dict[str, Any],
    ) -> Any:
        self.client = data.get("moderation_client")

        if not self.client:
            return await handler(event, data)

        user_id = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
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
