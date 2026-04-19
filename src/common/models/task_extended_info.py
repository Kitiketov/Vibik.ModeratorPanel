from typing import List, Optional

from pydantic import AnyHttpUrl, BaseModel, ConfigDict


class TaskExtendedInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    description: str
    photosRequired: int
    examplePhotos: Optional[List[AnyHttpUrl]] = []
    userPhotos: Optional[List[AnyHttpUrl]] = []
