from collections import Counter

from .base import BaseMetric
from src.utils.segment import Segment
from src.modules.analysis.schemas import (SegmentPaceMetrics, TurnTransition, PaceTrendPoint, PaceGlobalAnalysis,
                                          ReplicaType, PauseType)


class PaceAnalysis(BaseMetric):
    def calculate(self, segments: list[Segment], **kwargs) -> PaceGlobalAnalysis:
        all_replicas_type = [self._classify_replica(s).category for s in segments]
        # total_short_replicas = sum(1 for replica in all_replicas_type if replica == ReplicaType.REACTIVE)
        # total_standard_replicas = sum(1 for r in all_replicas_type if r == ReplicaType.STANDARD)
        # total_extended_replicas = sum(1 for r in all_replicas_type if r == ReplicaType.EXTENDED)
        total_monologue_replicas = sum(1 for r in all_replicas_type if r == ReplicaType.MONOLOGUE)

        all_transitions = self._analyze_all_transitions(segments)
        all_transitions_type = [pause.pause_category for pause in all_transitions]
        total_long_pauses = sum(1 for p in all_transitions_type if p == PauseType.LONG_PAUSE)
        total_small_pauses = sum(1 for p in all_transitions_type if p == PauseType.SMALL)

        pace_trends = self._generate_pace_trends(segments)
        return PaceGlobalAnalysis(
            total_monologues=total_monologue_replicas,
            total_long_pauses=total_long_pauses,
            total_instant_responses=total_small_pauses,
            pace_graph=pace_trends
        )
        pass

    def _classify_replica(self, segment: Segment) -> SegmentPaceMetrics:
        segment_duration_ms = segment.total_ms_end - segment.total_ms_start
        total_words = 0
        if segment.nlp_data:
            total_words = sum(
                1
                for sentence in segment.nlp_data
                for token in sentence
                if token.get("upos") != "PUNCT"
            )

        duration_seconds = (segment.total_ms_end - segment.total_ms_start) / 1000
        if total_words <= 3:
            replica_type = ReplicaType.REACTIVE
        elif total_words <= 15:
            replica_type = ReplicaType.STANDARD
        elif total_words <= 40:
            replica_type = ReplicaType.EXTENDED
        elif round(segment_duration_ms / 1000) >= 30:
            replica_type = ReplicaType.MONOLOGUE
        else:
            replica_type = ReplicaType.EXTENDED

        return SegmentPaceMetrics(word_count=total_words,
                                  duration_sec=duration_seconds,
                                  category=replica_type)

    def _calculate_transition(self, prev_segment: Segment, curr_segment: Segment) -> TurnTransition:
        pause_ms = (curr_segment.total_ms_start - prev_segment.total_ms_end)
        if pause_ms <= 200:
            pause_type = PauseType.SMALL
        elif pause_ms <= 1000:
            pause_type = PauseType.NORMAL_PAUSE
        elif pause_ms <= 2000:
            pause_type = PauseType.HESITATION
        else:
            pause_type = PauseType.LONG_PAUSE
        return TurnTransition(duration_seconds=pause_ms / 1000,
                              pause_category=pause_type)

    def _analyze_all_transitions(self, segments: list[Segment]) -> list[TurnTransition]:
        transitions = []
        for i in range(1, len(segments)):
            prev = segments[i - 1]
            curr = segments[i]
            transition = self._calculate_transition(prev, curr)
            transitions.append(transition)

        return transitions

    def _generate_pace_trends(self, segments: list[Segment], window_seconds: int = 60, step_seconds: int = 30) -> list[PaceTrendPoint]:
        total_movie_duration_ms = segments[-1].total_ms_end
        window_ms = window_seconds * 1000
        step_ms = step_seconds * 1000

        all_transitions = self._analyze_all_transitions(segments)  # pauses

        current_window_end_time_ms = window_ms
        trends = []
        while current_window_end_time_ms <= total_movie_duration_ms:
            # get all segments in the current window
            window_start_ms = current_window_end_time_ms - window_ms
            window_segments = [s for s in segments if s.total_ms_start >= window_start_ms and s.total_ms_end <= current_window_end_time_ms]

            # calculate pace trend point for this window
            curr_pace_trend_point = self._calculate_pace_trend_point_for_window(window_segments, segments,
                                                                                all_transitions, window_start_ms,
                                                                                current_window_end_time_ms)
            trends.append(curr_pace_trend_point)

            current_window_end_time_ms += step_ms

        return trends

    def _calculate_pace_trend_point_for_window(self, window_segments: list[Segment], segments: list[Segment],
                                               all_transitions: list[TurnTransition],
                                               window_start_ms: int, window_end_ms: int) -> (PaceTrendPoint | None):
        if not window_segments:  # the complete silence for the whole window
            return PaceTrendPoint(timestamps_total_ms=window_end_ms,
                                  total_local_words=0,
                                  silence_percentage=100,
                                  dominant_replica_type=None,
                                  dominant_pause_type=None)

        window_duration_seconds = (window_end_ms - window_start_ms) / 1000

        classified_replicas = [self._classify_replica(s) for s in window_segments]  # segment pace metrics object
        total_words_in_window = sum(replica.word_count for replica in classified_replicas)

        first_seg_index = segments.index(window_segments[0])
        last_seg_index = segments.index(window_segments[-1])

        window_transitions = all_transitions[first_seg_index:last_seg_index]  # those transitions in the given window

        all_replicas_types = [segment.category for segment in classified_replicas]
        dominant_replica_type, _ = Counter(all_replicas_types).most_common(1)[0]

        dominant_pause_type = None
        if window_transitions:  # there are pauses
            all_pauses_types = [p.pause_category for p in window_transitions]
            dominant_pause_type, _ = Counter(all_pauses_types).most_common(1)[0]

        total_silence_seconds = sum(transition.duration_seconds for transition in window_transitions)
        silence_percentage = (total_silence_seconds / window_duration_seconds) * 100

        return PaceTrendPoint(timestamps_total_ms=window_end_ms,
                              total_local_words=total_words_in_window,
                              silence_percentage=silence_percentage,
                              dominant_replica_type=dominant_replica_type,
                              dominant_pause_type=dominant_pause_type)
