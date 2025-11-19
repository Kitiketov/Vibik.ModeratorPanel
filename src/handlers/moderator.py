from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.types import Message, ReactionTypeEmoji

from src.api.photo_client import ModerationClient
from src.keyboards.common_kb import get_next_kb, create_moderator_kb
from src.states import moderator_state
from src.states.actions import Actions
from src.texts.common_text import next_photo

router = Router(name=__name__)

join_to_event_prefix = "join_to_event-"
join_to_event_postfix = "end_invitation"


async def set_reaction(message: Message) -> None:
    """
    Устанавливает реакцию 👍 на сообщение пользователя.

    Args:
        message (Message): Объект сообщения от пользователя.
    """
    await message.bot.set_message_reaction(
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
async def show_next_photo(message: Message, moderation_client: ModerationClient):
    try:
        task = await moderation_client.next()
        print(task)

        if task is None:
            await message.answer("Нет фотографий для модерации")
            return

        text = task.info()
        media = []
        for i, p in enumerate(task.extendedInfo.userPhotos):
            url = str(p)
            if i == 0:
                media.append(InputMediaPhoto(media=url, caption=text))
            else:
                media.append(InputMediaPhoto(media=url))

        a = await message.answer_media_group(media=media)
        print(a[0].message_id)
        kb = create_moderator_kb(task.taskId)
        await message.answer("Действие с задачей:", reply_markup=kb,reply_to_message_id=a[0].message_id)

    except Exception as e:
        await message.answer(f"Ошибка при получении фото: {e}")
        print(f"Error in show_next_photo: {e}")


@router.callback_query(
    moderator_state.ModeratorFactory.filter(F.action == Actions.APPROVE_PHOTO)
)
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
        await callback.message.reply_to_message.delete()
        await callback.message.delete()


@router.callback_query(
    moderator_state.ModeratorFactory.filter(F.action == Actions.REJECT_PHOTO)
)
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
        await callback.message.delete()
