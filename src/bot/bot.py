from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.bot.handlers import metrics, moderator
from src.bot.middleware import ModerationClientMiddleware, ModeratorAuthMiddleware
from src.moderation.client import ModerationClient


def create_dispatcher(moderation_client: ModerationClient) -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())

    client_middleware = ModerationClientMiddleware(moderation_client)
    dp.message.middleware(client_middleware)
    dp.callback_query.middleware(client_middleware)

    dp.message.middleware(ModeratorAuthMiddleware())
    dp.callback_query.middleware(ModeratorAuthMiddleware())

    dp.include_routers(
        moderator.router,
        metrics.router,
    )

    return dp


async def run_bot(bot: Bot, moderation_client: ModerationClient) -> None:
    dp = create_dispatcher(moderation_client)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
