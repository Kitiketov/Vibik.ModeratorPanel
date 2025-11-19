from pydantic import BaseModel, ConfigDict,AnyHttpUrl
from typing import List, Optional

class TaskExtendedInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    description: str
    photosRequired: int
    examplePhotos: Optional[List[AnyHttpUrl]] = []
    userPhotos: Optional[List[AnyHttpUrl]] = []
