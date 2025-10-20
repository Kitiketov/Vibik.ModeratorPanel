from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


from src.handlers import (
    moderator,

)


async def run_bot(token: str) -> None:
    bot = Bot(token)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_routers(
        moderator.router,

    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
