import asyncio

import uvicorn
from aiogram import Bot

from src.api.app import create_api_app
from src.bot.bot import run_bot
from src.core.config import settings
from src.moderation.client import ModerationClient, create_http_session


async def main() -> None:
    bot = Bot(settings.bot_token)
    session = await create_http_session()
    moderation_client = ModerationClient(
        base_url=str(settings.api_base),
        session=session,
    )
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
        await run_bot(bot, moderation_client)
    finally:
        server.should_exit = True
        await api_task
        await session.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
