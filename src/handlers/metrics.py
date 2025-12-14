from aiogram import Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, Message

from src.api.photo_client import ModerationClient
from src.keyboards.common_kb import get_next_kb
from src.utilities.metrics_visualization import (
    build_metrics_visualization,
    format_average_time,
    format_duration_minutes,
)

router = Router(name=__name__)

@router.message(Command("metrics"))
async def metrics_handler(message: Message, moderation_client: ModerationClient) -> None:
    try:
        metrics = await moderation_client.metrics()
    except Exception as exc:  # pragma: no cover - сеть/апи
        print(f"Error loading metrics: {exc}")
        await message.answer("Не удалось получить метрики, попробуйте позже.")
        return

    if metrics is None or len(metrics.root) == 0:
        await message.answer("Метрик за последнюю неделю пока нет.", reply_markup=get_next_kb)
        return

    visualization = build_metrics_visualization(metrics.root)
    summary = visualization.summary

    caption = (
        "Метрики за последнюю неделю:\n"
        f"• Среднее сдач на пользователя: {summary.average_submissions_per_user:.2f}\n"
        f"• Замены от сдач: {summary.change_percent:.1f}%\n"
        f"• Среднее время сдачи (время суток): {format_average_time(summary.average_submit_minutes)}\n"
        f"• Среднее время между сдачами (ч/мин): {format_duration_minutes(summary.average_between_submits_minutes)}\n"
        f"• Всего сдач: {summary.submit_count}, замен: {summary.change_count}, пользователей: {summary.user_count}\n"
        "График: последние 4 недели (по неделям)"
    )
    photo = BufferedInputFile(visualization.image_bytes, filename=visualization.filename)
    await message.answer_photo(photo, caption=caption, reply_markup=get_next_kb)

