from src.utils.segment import Segment
from .base import BaseMetric


class GenderStatsMetric(BaseMetric):
    def calculate(self, segments: list[Segment], **kwargs) -> dict:
        return {
            "woman_time_minutes": self._all_replicas_time_in_minutes_by_gender(segments, "woman"),
            "man_time_minutes": self._all_replicas_time_in_minutes_by_gender(segments, "man")
        }

    def _all_replicas_time_in_minutes_by_gender(self, segments: list[Segment], gender: str) -> float:
        result = 0
        for seg in segments:
            if seg.gender == gender:
                replica_duration = seg.total_ms_end - seg.total_ms_start
                result += replica_duration
        return round(result / 60000, 2)

