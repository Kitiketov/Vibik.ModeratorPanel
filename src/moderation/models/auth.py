from pydantic import BaseModel


class ModeratorCheckResponse(BaseModel):
    authorized: bool