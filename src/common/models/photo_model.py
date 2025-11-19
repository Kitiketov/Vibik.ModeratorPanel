from pydantic import BaseModel, ConfigDict

class PhotoModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    url: str
