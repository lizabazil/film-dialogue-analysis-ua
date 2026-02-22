# implement the time overlap logic
# it goes through each reference segment
# finds all LLM segments that intersect with it
# groups them. For, example, if one LLM segment "covers" two reference segments, it creates a ComparisonPair object,
# where ref_texts is a list of two elements, and hyp_text is one.
from src.evaluation.schemas import EvalSegment, ComparisonPair
from collections import deque


class TimelineAligner:

    def __init__(self):
        pass

    def align(self, ref_segments: list[EvalSegment], hyp_segments: list[EvalSegment]) -> list[ComparisonPair]:
        aligned_pairs = []
        used_ref_indexes = set()
        used_hyp_indexes = set()

        # go through reference (manually annotated) and build a group of hyps segments for it
        for i, ref in enumerate(ref_segments):
            if i in used_ref_indexes:  # ommit if this reference segment was already paired
                continue

            group_ref_indices, group_hyp_indices = self._build_group(i, ref_segments, hyp_segments, used_ref_indexes,
                                                                 used_hyp_indexes)

            if group_ref_indices or group_hyp_indices:
                pair = self._create_comparison_pair(
                    [ref_segments[index] for index in group_ref_indices],
                    [hyp_segments[index] for index in group_hyp_indices]
                )
                aligned_pairs.append(pair)

        return aligned_pairs

    def _build_group(self, start_ref_index: int, ref_segments: list[EvalSegment], hyp_segments: list[EvalSegment],
                     used_refs: set[int],
                     used_hyps: set[int]) -> tuple[set, set]:
        """
        1. Take Ref -> finds all respective Hyps
        2. For each found Hyp -> finds all other Refs, which overlap with it.
        3. Repeats, until the group is formed.
        Args:
            start_ref_index:
            ref_segments:
            used_refs:
            used_hyps:

        Returns:

        """
        # sets for current group
        current_ref_indices = {start_ref_index}
        current_hyps_indices = set()

        refs_segments_to_check = deque([start_ref_index])  # deque for possible candidates of Refs for Hyps

        while refs_segments_to_check:
            current_ref_index = refs_segments_to_check.popleft()
            current_ref_segment = ref_segments[current_ref_index]

            # find all respective Hyps for given Reference segment
            for hyp_index, hyp_segment in enumerate(hyp_segments):
                if self._do_overlap(current_ref_segment, hyp_segment):  # there is an overlap

                    if hyp_index not in current_hyps_indices:
                        current_hyps_indices.add(hyp_index)

                        # go with found Hyp and find respective Refs for it
                        for i, ref_seg in enumerate(ref_segments):
                            if i not in current_ref_indices and self._do_overlap(ref_seg, hyp_segment):
                                current_ref_indices.add(i)
                                refs_segments_to_check.append(i)

        used_refs.update(current_ref_indices)
        used_hyps.update(current_hyps_indices)

        return current_ref_indices, current_hyps_indices

    def _do_overlap(self, first_seg: EvalSegment, second_seg: EvalSegment) -> bool:
        """
        Using formula: max(start_1, start_2) < min(end_1, end_2)
        Args:
            first_seg:
            second_seg:

        Returns:

        """
        return max(first_seg.start_ms, second_seg.start_ms) < min(first_seg.end_ms, second_seg.end_ms)

    def _create_comparison_pair(self, ref_segments: list[EvalSegment], hyp_segments: list[EvalSegment]) \
            -> ComparisonPair:
        return ComparisonPair(
            ref_segments=ref_segments,
            hyp_segments=hyp_segments,
        )
