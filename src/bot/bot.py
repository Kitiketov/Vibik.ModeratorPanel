from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.handlers import metrics, moderator
from src.bot.middleware import ModerationClientMiddleware, ModeratorAuthMiddleware


def create_dispatcher() -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())

    dp.message.middleware(ModerationClientMiddleware())
    dp.callback_query.middleware(ModerationClientMiddleware())

    dp.message.middleware(ModeratorAuthMiddleware())
    dp.callback_query.middleware(ModeratorAuthMiddleware())

    dp.include_routers(
        moderator.router,
        metrics.router,
    )

    return dp


async def run_bot(bot: Bot) -> None:
    dp = create_dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
