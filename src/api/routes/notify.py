import asyncio

from aiogram import Bot
from fastapi import APIRouter, Request

from src.api.schemas.notify import NotifyRequest, NotifyResponse, FailedNotification
from src.bot.keyboards.common_kb import get_next_kb
from src.bot.texts.common_text import new_task_notification

router = APIRouter()


async def _send_notifications(bot: Bot, moderator_ids: list[int], text: str) -> NotifyResponse:
    tasks = [
        bot.send_message(chat_id=moderator_id, text=text, reply_markup=get_next_kb) for moderator_id in moderator_ids
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    failed = []
    sent = 0

    for moderator_id, result in zip(moderator_ids, results):
        if isinstance(result, Exception):
            failed.append(FailedNotification(id=moderator_id, error=str(result)))
        else:
            sent += 1

    return NotifyResponse(sent=sent, failed=failed)


@router.post("/notify")
async def notify(payload: NotifyRequest, request: Request):
    bot: Bot = request.app.state.bot
    result = await _send_notifications(bot, payload.moderator_ids, new_task_notification)
    return result
