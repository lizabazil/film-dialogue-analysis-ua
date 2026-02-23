from src.utils.segment import Segment
from .base import BaseMetric
from collections import Counter


class SpeakerLexicon(BaseMetric):
    def calculate(self, segments: list[Segment], **kwargs) -> dict:
        return {
            "top_man_lemmas": self._get_most_common_lemmas(segments, "man"),
            "top_woman_lemmas": self._get_most_common_lemmas(segments, "woman"),
            "top_all_gender_lemmas": self._get_most_common_lemmas(segments)
        }

    def _get_most_common_lemmas(self, segments: list[Segment], gender: str = None, top_n=20) -> list:
        words = []
        allowed_part_of_speech = ["NOUN", "ADJ", "VERB", "ADV", "PROPN"]

        for seg in segments:
            if gender is None or seg.gender == gender:
                if seg.nlp_data:
                    for sentence in seg.nlp_data:
                        for token in sentence:
                            token_pos = token.get("upos")
                            if token_pos in allowed_part_of_speech:
                                lemma = token.get("lemma")
                                words.append(lemma)

        count = Counter(words)
        return [{"word": w, "count": c} for w, c in count.most_common(top_n)]
