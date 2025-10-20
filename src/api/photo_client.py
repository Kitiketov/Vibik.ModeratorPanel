from src.common.photo import Photo
from src.common.task import Task

fake_task = Task("honey_cars",212,"Медовые машины","Cфоткать 5 желтых машин")
fake_photo = Photo(r"src\temp\022952.png","kitiket",fake_task)

class PhotoClient:
    @staticmethod
    def get_next_photo():
        # запрос к ручке
        photo = fake_photo
        return photo
