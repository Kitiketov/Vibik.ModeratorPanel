from pydantic import BaseModel, ConfigDict, RootModel

from src.common.models.metric_model import MetricModel


class MetricsListModel(RootModel[list[MetricModel]]):
    pass