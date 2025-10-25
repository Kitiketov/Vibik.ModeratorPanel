from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup

from src.states.moderator_state import ModeratorFactory
from src.texts.common_text import cancel, ok, next_photo, approve, reject
from src.states.actions import Actions

ok_kb: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=ok,
                callback_data="ok",
            )
        ]
    ]
)

cancel_kb: InlineKeyboardMarkup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text=cancel,
                action="cancel",
            )
        ]
    ]
)


def create_moderator_kb(user_task_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=approve,
                    callback_data=ModeratorFactory(
                        action=Actions.APPROVE_PHOTO, user_task_id=user_task_id
                    ).pack(),
                ),
                InlineKeyboardButton(
                    text=reject,
                    callback_data=ModeratorFactory(
                        action=Actions.REJECT_PHOTO, user_task_id=user_task_id
                    ).pack(),
                ),
            ]
        ]
    )


get_next_kb: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=next_photo)]]
)
