from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict
from src.common.models.task_extended_info import TaskExtendedInfo
from src.texts.moderation_text import photo_info

class ModerationTask(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    userTaskId: int
    taskId: str
    name: str
    tags: list[str]
    extendedInfo: TaskExtendedInfo|None

    def info(self):
        return photo_info.format(self.name, self.extendedInfo.description, ", ".join(map(str, self.tags)))