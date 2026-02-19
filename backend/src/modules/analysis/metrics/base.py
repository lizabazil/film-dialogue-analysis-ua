from abc import ABC, abstractmethod
from typing import Any
from src.utils.segment import Segment


class BaseMetric(ABC):

    @abstractmethod
    def calculate(self, segments: list[Segment], **kwargs) -> Any:
        pass
