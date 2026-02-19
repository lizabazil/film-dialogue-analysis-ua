from typing import Any

from src.utils.segment import Segment
from .base import BaseMetric


class GenderStatsMetric(BaseMetric):
    def calculate(self, segments: list[Segment], **kwargs) -> Any:
        pass
