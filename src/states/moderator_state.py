from aiogram.filters.callback_data import CallbackData


class ModeratorFactory(CallbackData, prefix="moderator_data"):
    action: str
    user_task_id: str
