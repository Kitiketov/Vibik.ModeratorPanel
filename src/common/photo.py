from src.common.task import Task
from src.texts.moderation_text import photo_info


class Photo:
    def __init__(self, url: str, task: Task):
        self.url = url
        self.task = task

    def Info(self):
        return photo_info.format(self.task.name, self.task.description, self.task.tags)
