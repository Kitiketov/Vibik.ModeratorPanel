class Task:
    def __init__(self, task_id,user_task_id,name,description,tags=None):
        self.task_id = task_id
        self.user_task_id = user_task_id
        self.name = name
        self.description = description
        self.tags = tags