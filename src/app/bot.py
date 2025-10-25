from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.config import settings
from src.middleware import ModerationClientMiddleware
from src.auth_middleware import ModeratorAuthMiddleware
from src.handlers import (
    moderator,

)


async def run_bot(token: str) -> None:
    bot = Bot(token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(ModerationClientMiddleware())
    dp.callback_query.middleware(ModerationClientMiddleware())

    dp.message.middleware(ModeratorAuthMiddleware())
    dp.callback_query.middleware(ModeratorAuthMiddleware())

    dp.include_routers(
        moderator.router,

    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
