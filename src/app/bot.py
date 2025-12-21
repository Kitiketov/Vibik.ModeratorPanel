from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.app.notify_server import start_notify_server, stop_notify_server
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

    notify_runner = await start_notify_server(bot)
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await stop_notify_server(notify_runner)
