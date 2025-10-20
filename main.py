import asyncio

from src.app.bot import run_bot
from src.Settings.settings import Settings

settings: Settings = Settings()


async def main() -> None:
    await run_bot(settings.bot_token)



if __name__ == "__main__":
    asyncio.run(main())
