from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InaccessibleMessage, InputMediaDocument, Message, ReactionTypeEmoji

from src.bot.keyboards.common_kb import create_moderator_kb, get_next_kb
from src.bot.states import moderator_state
from src.bot.states.actions import Actions
from src.bot.texts.common_text import next_photo
from src.bot.texts.moderation_text import photo_info
from src.moderation.client import ModerationClient

router = Router(name=__name__)

join_to_event_prefix = "join_to_event-"
join_to_event_postfix = "end_invitation"


async def set_reaction(message: Message) -> None:
    """
    Устанавливает реакцию 👍 на сообщение пользователя.

    Args:
        message (Message): Объект сообщения от пользователя.
    """
    bot = message.bot
    if bot is None:
        return
    await bot.set_message_reaction(
        chat_id=message.chat.id,
        message_id=message.message_id,
        reaction=[ReactionTypeEmoji(emoji="👍")],
    )


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext) -> None:
    print(message.text)
    # replay: InlineKeyboardMarkup = start_menu_kb.start_kb
    await message.answer("Привет", reply_markup=get_next_kb)


@router.message(F.text == next_photo)
@router.message(Command("next_photo"))
async def show_next_photo(message: Message, moderation_client: ModerationClient):
    try:
        task = await moderation_client.next()
        print(task)

        if task is None:
            await message.answer("Нет фотографий для модерации")
            return

        text = photo_info.format(task.name, task.extendedInfo.description, ", ".join(map(str, task.tags)))
        media: list[InputMediaDocument] = []
        a = None
        for i, p in enumerate(task.extendedInfo.userPhotos or []):
            url = str(p)
            if i != 0 and i % 10 == 0:
                a = await send_with_repl(a, media, message)
                media = []
            media.append(InputMediaDocument(media=url, caption=text if i % 10 == 0 else None))

        a = await send_with_repl(a, media, message)

        print(a[0].message_id)
        kb = create_moderator_kb(task.userTaskId)
        await message.answer("Действие с задачей:", reply_markup=kb, reply_to_message_id=a[0].message_id)

    except Exception as e:
        await message.answer(f"Ошибка при получении фото: {e}")
        print(f"Error in show_next_photo: {e}")


async def send_with_repl(a, media, message):
    if a is None:
        a = await message.answer_media_group(media=media)
    else:
        a = await message.answer_media_group(media=media, reply_to_message_id=a[0].message_id)
    return a


@router.callback_query(moderator_state.ModeratorFactory.filter(F.action == Actions.APPROVE_PHOTO))
async def approve_handler(
    callback: CallbackQuery,
    callback_data: moderator_state.ModeratorFactory,
    state: FSMContext,
    moderation_client: ModerationClient,
) -> None:
    try:
        success = await moderation_client.approve(callback_data.user_task_id)
        if success:
            await callback.answer("Фото одобрено ✅")
        else:
            await callback.answer("Ошибка при одобрении фото ❌")
    except Exception as e:
        await callback.answer(f"Ошибка: {e}")
        print(f"Error in approve_handler: {e}")
    finally:
        await _delete_related_messages(callback.message)


@router.callback_query(moderator_state.ModeratorFactory.filter(F.action == Actions.REJECT_PHOTO))
async def reject_handler(
    callback: CallbackQuery,
    callback_data: moderator_state.ModeratorFactory,
    state: FSMContext,
    moderation_client: ModerationClient,
) -> None:
    try:
        success = await moderation_client.reject(callback_data.user_task_id)
        if success:
            await callback.answer("Фото отклонено ❌")
        else:
            await callback.answer("Ошибка при отклонении фото ❌")
    except Exception as e:
        await callback.answer(f"Ошибка: {e}")
        print(f"Error in reject_handler: {e}")
    finally:
        await _delete_related_messages(callback.message, delete_reply=False)


async def _delete_related_messages(
    message: Message | InaccessibleMessage | None,
    *,
    delete_reply: bool = True,
) -> None:
    """Delete callback message and optionally replied message, if accessible."""
    if not isinstance(message, Message):
        return

    if delete_reply and isinstance(message.reply_to_message, Message):
        await message.reply_to_message.delete()

    await message.delete()
