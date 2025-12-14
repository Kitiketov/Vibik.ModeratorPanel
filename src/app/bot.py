from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from src.middleware import ModerationClientMiddleware, ModeratorAuthMiddleware
from src.handlers import (
    moderator,
    metrics,
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
        metrics.router,
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
