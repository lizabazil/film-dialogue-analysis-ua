from src.utils.segment import Segment
from src.utils.time_utils import TimeUtils
import re


class SegmentNormalizer:

    def normalize(self, segments: list[Segment]) -> list[Segment]:
        """
        Calls two methods to:
        1. Merge two replicas if the second replica is a continuation of the first.
        2. Merge close replicas if they have the same speaker and the gap between them is less than the specified gap.
        Args:
            segments: Input segments to be normalized.

        Returns:
            list[Segment]: Normalized replicas.
        """
        if not segments:
            return []
        segments = self.merge_broken_sentences(segments)
        segments = self.merge_close_segments(segments)
        return segments

    def merge_broken_sentences(self, segments: list[Segment]) -> list[Segment]:
        """
        Works in case if one replica is split into two segments (when there is no end of sentence in first
        replica, and this sentence continues in another replica (and the speaker is the same)).
        Args:
            segments:

        Returns:

        """
        if not segments:
            return []

        merged_segments = []
        # will be match with !.?  only if those symbols are at the end of the string
        end_of_sentence_chars = re.compile(r"[!.?]+$")

        for s in segments:
            if not merged_segments:
                merged_segments.append(s)
                continue

            prev_segment = merged_segments[-1]
            prev_speech = prev_segment.speech.strip()

            should_merge = (
                prev_segment.speaker_id == s.speaker_id and prev_speech
                and (not end_of_sentence_chars.search(prev_speech))
            )

            if should_merge:
                prev_segment.speech = f"{prev_speech} {s.speech.strip()}"

                prev_segment.end_h = s.end_h
                prev_segment.end_m = s.end_m
                prev_segment.end_s = s.end_s
                prev_segment.end_ms = s.end_ms

                prev_segment.add_nlp_data(s.nlp_data)
            else:
                merged_segments.append(s)

        return merged_segments

    def merge_close_segments(self, segments: list[Segment], gap_duration_in_seconds: float = 2) -> list[Segment]:
        """
        Merges consecutive segments from the same speaker if they are separated by a short pause.

        This method is designed to reconstruct continuous speech flow. It checks the time gap between the end of one
        segment and the start of the next. If the gap is less than the predefined threshold (currently 2 seconds) and
        the speaker is the same, the segments are joined into one.

        Args:
            segments (list[Segment]): An ordered list of transcript segments to process.
            gap_duration_in_seconds (float): A boundary value for gap duration. If the pause between two segments >=
            this value, then those segments WILL NOT be joined, even having the same speaker.
        Returns:
            list[Segment]: An edited list of segments where close replicas have been joined (their timecodes and nlp_data
            were properly changed).
        """
        if not segments:
            return []

        merged_segments = []
        # join two replicase only if pause between them is no more than 2 seconds
        for current_segment in segments:
            if not merged_segments:
                merged_segments.append(current_segment)
                continue

            prev_segment = merged_segments[-1]

            if prev_segment.speaker_id != current_segment.speaker_id:
                merged_segments.append(current_segment)
                continue

            gap_duration = TimeUtils.get_gap_duration(prev_segment, current_segment)
            if gap_duration < gap_duration_in_seconds:  # small pause, join two segments
                prev_segment.speech += f" {current_segment.speech}"
                prev_segment.end_h = current_segment.end_h
                prev_segment.end_m = current_segment.end_m
                prev_segment.end_s = current_segment.end_s
                prev_segment.end_ms = current_segment.end_ms

                prev_segment.add_nlp_data(current_segment.nlp_data)
            else:
                merged_segments.append(current_segment)

        return merged_segments
