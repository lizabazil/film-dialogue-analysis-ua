from src.utils.segment import Segment
from .base import BaseMetric
from src.modules.post_processing.normalizers import SegmentNormalizer


class GenderStatsMetric(BaseMetric):
    def calculate(self, segments: list[Segment], **kwargs) -> dict:
        total_replicas_woman = self._get_number_of_replicas_by_gender(segments, "woman")
        total_replicas_man = self._get_number_of_replicas_by_gender(segments, "man")

        total_words_woman = self._get_total_words_per_gender(segments, "woman")
        total_words_man = self._get_total_words_per_gender(segments, "man")
        return {
            "woman_time_minutes": self._all_replicas_time_in_minutes_by_gender(segments, "woman"),
            "man_time_minutes": self._all_replicas_time_in_minutes_by_gender(segments, "man"),
            "woman_replicas": total_replicas_woman,
            "man_replicas": total_replicas_man,

            # number of all words of the gender / number of all replicas by this gender
            "avg_words_per_replica_woman": total_words_woman / total_replicas_woman,
            "avg_words_per_replica_man": total_words_man / total_replicas_man,
            "bechdel_test": ...  # TODO: complete
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

    def _get_total_words_per_gender(self, segments: list[Segment], gender: str) -> int:
        """
        Get total number of words for the given gender (without punctuation).
        Args:
            segments: List of segments from the whole movie.
            gender: Gender to find total words for.

        Returns:
            int: Number of all words, without punctuation.
        """
        return sum(
            1
            for seg in segments if seg.gender == gender and seg.nlp_data
            for sentence in seg.nlp_data
            for token in sentence
            if token.get("upos") != "PUNCT"
        )
