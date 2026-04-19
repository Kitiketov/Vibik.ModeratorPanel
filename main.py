import asyncio

import uvicorn
from aiogram import Bot

from src.api.app import create_api_app
from src.bot.bot import run_bot
from src.core.config import settings


async def main() -> None:
    bot = Bot(settings.bot_token)
    app = create_api_app(bot)

    config = uvicorn.Config(
        app=app,
        host=settings.notify_host,
        port=settings.notify_port,
        log_level="info",
    )
    server = uvicorn.Server(config)
    api_task = asyncio.create_task(server.serve())

    try:
        await run_bot(bot)
    finally:
        server.should_exit = True
        await api_task
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
