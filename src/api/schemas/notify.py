from pydantic import BaseModel


class NotifyRequest(BaseModel):
    moderator_ids: list[int]


class FailedNotification(BaseModel):
    id: int
    error: str


class NotifyResponse(BaseModel):
    sent: int
    failed: list[FailedNotification]
