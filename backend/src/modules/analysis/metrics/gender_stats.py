from src.utils.segment import Segment
from .base import BaseMetric
from src.modules.post_processing.normalizers import SegmentNormalizer
from src.modules.analysis.metrics.pace_analysis import PaceAnalysis


class GenderStatsMetric(BaseMetric):
    def __init__(self):
        self.segment_normalizer = SegmentNormalizer()

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
            "bechdel_test": self._passes_bechdel_test(segments)
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
        joined_by_same_speaker = self.segment_normalizer.merge_close_segments(segments, float('inf'))
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

    def _passes_bechdel_test(self, segments: list[Segment]) -> dict:
        points_passed = 0

        dialogue_groups = self._form_dialogue_groups(segments)
        women_speaking_to_each_other = self._filter_women_speaking_to_each_other(dialogue_groups)

        if women_speaking_to_each_other:
            points_passed += 2

            blocks_with_women_speaking_to_each_other = self._get_dialogue_blocks_with_only_women_speaking(
                women_speaking_to_each_other)

            not_talking_about_men = self._are_women_talking_beside_man(blocks_with_women_speaking_to_each_other)
            if not_talking_about_men:
                points_passed += 1
            return {"passed_bechdel_test": not_talking_about_men, "passed_points": points_passed}
        return {"passed_bechdel_test": False, "passed_points": points_passed}

    def _form_dialogue_groups(self, segments: list[Segment], gap_seconds: int = 5) -> list[list[Segment]]:
        """
        Forms dialogue groups, based on the gap between replicas. If the gap >= 'gap_seconds', then it is treated
        as the start of a new dialogue, which will be processed independently later in the Bechdel test.
        Args:
            segments:

        Returns:

        """
        if not segments:
            return []

        all_groups = []
        current_group = [segments[0]]  # adding the very first segment to the first group

        for i, seg in enumerate(segments[1:]):
            curr_segment_start_ms = seg.total_ms_start
            prev_segment_end_ms = current_group[-1].total_ms_end
            ms_difference = curr_segment_start_ms - prev_segment_end_ms
            seconds_difference = ms_difference // 1000  # floor division

            if seconds_difference <= gap_seconds:  # current segment will be added to the current group
                current_group.append(seg)
            else:  # current segment cannot be added to the current group
                if current_group:
                    all_groups.append(current_group)
                current_group = [seg]

        if current_group:
            all_groups.append(current_group)

        return all_groups

    def _filter_women_speaking_to_each_other(self, segments_groups: list[list[Segment]]) -> list[list[Segment]]:
        """
        To filter those groups of segments, where at least two women speak to each other (in other words, their
        replicas are located right next to each other). Those groups are merged (so the neighboring replicas by
        the same speaker are merged).
        Args:
            segments_groups:

        Returns:

        """
        if not segments_groups:
            return []

        final_groups = []
        for group in segments_groups:
            # squeeze segments, so there consequent replicas by the same speakers are together in one replica
            group_merged = self.segment_normalizer.merge_close_segments(group, float('inf'))
            prev_seg = group_merged[0]
            for curr_seg in group_merged[1:]:
                if prev_seg.gender == "woman" and curr_seg.gender == "woman":
                    final_groups.append(group_merged)
                    break
                else:
                    prev_seg = curr_seg

        return final_groups

    def _get_dialogue_blocks_with_only_women_speaking(self, segment_groups: list[list[Segment]]) -> list[list[Segment]]:
        """
        To get blocks where at least two women speak to each other.
        Args:
            segment_groups: Must be with replicas already merged (so the neighboring replicas by the same speaker are
            already in the same segment).

        Returns:

        """
        if not segment_groups:
            return []

        all_female_blocks = []
        for group in segment_groups:
            current_female_block = []
            for seg in group:
                if seg.gender == "woman":
                    current_female_block.append(seg)
                else:  # man speaking
                    if len(current_female_block) >= 2:
                        all_female_blocks.append(current_female_block)
                    current_female_block = []

            if len(current_female_block) >= 2:
                all_female_blocks.append(current_female_block)

        return all_female_blocks

    def _are_women_talking_beside_man(self, segment_groups: list[list[Segment]]) -> bool:
        """
        Checks third Bechdel condition: the movie passes it if women are talking about something besides a man.
        Args:
            segment_groups:

        Returns:

        """
        for group in segment_groups:
            # check if there is enough words in the group (to avoid very short phrases like greetings)
            total_words = sum(PaceAnalysis.classify_replica(s).word_count for s in group)
            if total_words <= 6:
                return False
            if not self._is_group_about_man(group):
                return True
        return False

    def _is_group_about_man(self, segment_group: list[Segment]) -> bool:
        male_lemmas_list = ["чоловік", "хлопець", "батько", "син", "брат", "наречений", "тато", "пан"]
        male_pronouns_list = ["він", "його", "йому", "ним", "нього", "ньому"]

        common_human_verbs = ["казати", "сказати", "говорити", "обіцяти", "думати", "хотіти", "працювати", "купувати",
                              "кохати", "любити", "телефонувати", "дзвонити", "писати", "читати", "знати"]

        for seg in segment_group:
            if not seg.nlp_data:
                continue

            for sentence in seg.nlp_data:
                verbs_with_subjects_ids = [t.get("head") for t in sentence if t.get("deprel") == "nsubj"]

                for token in sentence:
                    lemma = token.get("lemma")
                    deprel = token.get("deprel", "")
                    feats = token.get("feats", {})
                    token_id = token.get("id")

                    if lemma in male_lemmas_list:
                        return True
                    if lemma in male_pronouns_list:
                        if feats.get("Animacy") == "Anim" and feats.get("Gender") == "Masc":
                            return True

                    # there is a nominal subject in the sentence and it was marked as male
                    if deprel == "nsubj" and feats.get("Gender") == "Masc" and feats.get("Animacy") == "Anim":
                        return True

                    # if it's a verb in the past tense, and it was marked as a male
                    if token.get("upos") == "VERB" and feats.get("Tense") == "Past" and feats.get("Gender") == "Masc":
                        # there is only a verb, with subject for it
                        if token_id not in verbs_with_subjects_ids:
                            if lemma in common_human_verbs:
                                return True

        return False
