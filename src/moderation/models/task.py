from __future__ import annotations

from pydantic import AnyHttpUrl, BaseModel, ConfigDict


class PhotoModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    url: str


class TaskExtendedInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    description: str
    photosRequired: int
    examplePhotos: list[AnyHttpUrl] = []
    userPhotos: list[AnyHttpUrl] = []


class ModerationTask(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    userTaskId: int
    taskId: str
    name: str
    tags: list[str]
    extendedInfo: TaskExtendedInfo
