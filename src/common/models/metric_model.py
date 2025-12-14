from pydantic import BaseModel, ConfigDict
from datetime import datetime
import enum
class MetricType(enum.Enum):
    Submit =0
    Change =1



class MetricModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)
    id:int
    username:str
    type:MetricType
    time: datetime

