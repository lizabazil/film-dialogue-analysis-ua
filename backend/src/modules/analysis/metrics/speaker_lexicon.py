from src.utils.segment import Segment
from .base import BaseMetric
from collections import Counter


class SpeakerLexicon(BaseMetric):
    def calculate(self, segments: list[Segment], **kwargs) -> dict:
        # getting nouns, adjectives, verbs, adverbs, proper nouns, pronouns, numerical (independent parts of speech)
        part_of_speech = ["NOUN", "ADJ", "VERB", "ADV", "PROPN", "PRON", "NUM"]
        return {
            "top_man_lemmas": self._get_most_common_lemmas(segments, part_of_speech, "man"),
            "top_woman_lemmas": self._get_most_common_lemmas(segments, part_of_speech, "woman"),
            "top_all_gender_lemmas": self._get_most_common_lemmas(segments, part_of_speech),
            "top_nouns_all_genders": self._get_most_common_lemmas(segments, ["NOUN"]),
            "top_verbs_all_genders": self._get_most_common_lemmas(segments, ["VERB"]),
            "top_adjectives_all_genders": self._get_most_common_lemmas(segments, ["ADJ"])
        }

    def _get_most_common_lemmas(self, segments: list[Segment], allowed_parts_of_speech: list[str], gender: str = None,
                                top_n=20) -> list:
        words = []

        for seg in segments:
            if gender is None or seg.gender == gender:
                if seg.nlp_data:
                    for sentence in seg.nlp_data:
                        for token in sentence:
                            token_pos = token.get("upos")
                            if token_pos in allowed_parts_of_speech:
                                lemma = token.get("lemma")
                                words.append(lemma)

        count = Counter(words)
        return [{"word": w, "count": c} for w, c in count.most_common(top_n)]
