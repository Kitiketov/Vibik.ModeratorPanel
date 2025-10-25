class Task:
    def __init__(self, user_task_id, name, description, tags=None):
        self.user_task_id = user_task_id
        self.name = name
        self.description = description
        self.tags = tags
