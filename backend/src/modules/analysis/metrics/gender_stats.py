from src.utils.segment import Segment
from .base import BaseMetric
from src.modules.post_processing.normalizers import SegmentNormalizer


class GenderStatsMetric(BaseMetric):
    def calculate(self, segments: list[Segment], **kwargs) -> dict:
        return {
            "woman_time_minutes": self._all_replicas_time_in_minutes_by_gender(segments, "woman"),
            "man_time_minutes": self._all_replicas_time_in_minutes_by_gender(segments, "man"),
            "woman_replicas": self._get_number_of_replicas_by_gender(segments, "woman"),
            "man_replicas": self._get_number_of_replicas_by_gender(segments, "man")
        }

    def _all_replicas_time_in_minutes_by_gender(self, segments: list[Segment], gender: str) -> float:
        result = 0
        for seg in segments:
            if seg.gender == gender:
                replica_duration = seg.total_ms_end - seg.total_ms_start
                result += replica_duration
        return round(result / 60000, 2)

    def _get_number_of_replicas_by_gender(self, segments: list[Segment], gender: str) -> int:
        # first of all, join each speaker replica
        joined_by_same_speaker = SegmentNormalizer().merge_close_segments(segments, float('inf'))
        res = sum(seg.gender == gender for seg in joined_by_same_speaker)
        return res
