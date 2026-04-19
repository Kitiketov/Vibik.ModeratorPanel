from __future__ import annotations

import enum
from datetime import datetime

from pydantic import BaseModel, ConfigDict, RootModel


class MetricType(enum.Enum):
    Submit = 0
    Change = 1


class MetricModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, use_enum_values=True)

    id: int
    username: str
    type: MetricType
    time: datetime


class MetricsListModel(RootModel[list[MetricModel]]):
    pass
