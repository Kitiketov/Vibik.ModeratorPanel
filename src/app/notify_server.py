from __future__ import annotations

import asyncio
from typing import Any

from aiohttp import web
from aiogram import Bot

from src.config import settings
from src.keyboards.common_kb import get_next_kb
from src.texts.common_text import new_task_notification


def _normalize_ids(raw_ids: Any) -> list[int] | None:
    if not isinstance(raw_ids, list):
        return None

    normalized: list[int] = []
    for raw_id in raw_ids:
        if isinstance(raw_id, int):
            normalized.append(raw_id)
        elif isinstance(raw_id, str) and raw_id.isdigit():
            normalized.append(int(raw_id))
        else:
            return None
    return normalized


async def _send_notifications(bot: Bot, moderator_ids: list[int], text: str) -> dict[str, Any]:
    tasks = [
        bot.send_message(chat_id=moderator_id, text=text, reply_markup=get_next_kb)
        for moderator_id in moderator_ids
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    failed: list[dict[str, Any]] = []
    sent = 0
    for moderator_id, result in zip(moderator_ids, results):
        if isinstance(result, Exception):
            failed.append({"id": moderator_id, "error": str(result)})
        else:
            sent += 1

    return {"sent": sent, "failed": failed}


async def notify_handler(request: web.Request) -> web.Response:
    try:
        payload = await request.json()
    except Exception:
        return web.json_response({"detail": "invalid json"}, status=400)

    moderator_ids = _normalize_ids(payload.get("moderator_ids"))
    if moderator_ids is None or len(moderator_ids) == 0:
        return web.json_response(
            {"detail": "moderator_ids must be a non-empty list of int"},
            status=400,
        )

    text = new_task_notification

    bot: Bot = request.app["bot"]
    result = await _send_notifications(bot, moderator_ids, text)
    status = 200 if len(result["failed"]) == 0 else 207
    return web.json_response(result, status=status)


async def start_notify_server(bot: Bot) -> web.AppRunner:
    app = web.Application()
    app["bot"] = bot

    path = settings.notify_path
    if not path.startswith("/"):
        path = f"/{path}"
    app.router.add_post(path, notify_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, settings.notify_host, settings.notify_port)
    await site.start()
    print(f"Notify server started on {settings.notify_host}:{settings.notify_port}{path}")
    return runner


async def stop_notify_server(runner: web.AppRunner) -> None:
    await runner.cleanup()
