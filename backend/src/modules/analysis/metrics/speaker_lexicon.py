from src.utils.segment import Segment
from src.modules.analysis.schemas import TfIdf
from src.modules.analysis.metrics.constants import *
from .base import BaseMetric
from collections import Counter
import math


class SpeakerLexicon(BaseMetric):
    def calculate(self, segments: list[Segment], **kwargs) -> dict:
        all_parts_of_speech_and_propn = [POS_NOUN, POS_ADJECTIVE, POS_VERB, POS_ADVERB, POS_PROPER_NOUN, POS_PRON, POS_NUM]
        genders = [WOMAN_GENDER, MAN_GENDER]

        part_of_speech = [POS_NOUN, POS_ADJECTIVE, POS_VERB, POS_ADVERB, POS_PROPER_NOUN]
        return {
            "top_man_lemmas": self._get_most_common_lemmas(segments, part_of_speech, MAN_GENDER),
            "top_woman_lemmas": self._get_most_common_lemmas(segments, part_of_speech, WOMAN_GENDER),
            "top_all_gender_lemmas": self._get_most_common_lemmas(segments, part_of_speech),
            "top_nouns_all_genders": self._get_most_common_lemmas(segments, [POS_NOUN]),
            "top_verbs_all_genders": self._get_most_common_lemmas(segments, [POS_VERB]),
            "top_adjectives_all_genders": self._get_most_common_lemmas(segments, [POS_ADJECTIVE]),

            "pos_usage_by_genders": [{"gender": gender, "part_of_speech": pos,
                                      "percentage": self._get_percentage_of_part_of_speech_by_gender(segments, pos, gender)}
                                     for pos in all_parts_of_speech_and_propn for gender in genders],

            "tf_idf_by_genders": self._get_gender_tf_idf(segments)
        }

    def _get_most_common_lemmas(self, segments: list[Segment], allowed_parts_of_speech: list[str], gender: str = None,
                                top_n=None) -> list:
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

    def _get_percentage_of_part_of_speech_by_gender(self, segments: list[Segment], part_of_speech: str, gender: str) -> float:
        specific_pos_data = self._get_most_common_lemmas(segments, [part_of_speech], gender)
        count_given_pos = sum(item["count"] for item in specific_pos_data)
        all_pos = [POS_NOUN, POS_ADJECTIVE, POS_VERB, POS_ADVERB, POS_PROPER_NOUN, POS_PRON, POS_NUM]
        all_words_data = self._get_most_common_lemmas(segments, all_pos, gender)
        total_words_count = sum(item['count'] for item in all_words_data)
        if total_words_count == 0:
            return 0.0
        return (count_given_pos / total_words_count) * 100

    def _get_gender_tf_idf(self, segments: list[Segment]) -> list[TfIdf]:
        meaningful_pos = [POS_NOUN, POS_ADJECTIVE, POS_VERB, POS_ADVERB, POS_PROPER_NOUN, POS_PRON, POS_NUM]
        documents = {WOMAN_GENDER: [], MAN_GENDER: []}
        for seg in segments:
            curr_gender = seg.gender
            if curr_gender in documents and seg.nlp_data:
                for sentence in seg.nlp_data:
                    for token in sentence:
                        if token.get("upos") in meaningful_pos:
                            documents[curr_gender].append(token.get("lemma"))

        woman_counts = Counter(documents[WOMAN_GENDER])
        man_counts = Counter(documents[MAN_GENDER])

        totals = {
            WOMAN_GENDER: sum(woman_counts.values()),
            MAN_GENDER: sum(man_counts.values())
        }

        tf_idf_by_genders = []

        for gender in [WOMAN_GENDER, MAN_GENDER]:
            counts_for_current_gender = woman_counts if gender == WOMAN_GENDER else man_counts
            another_gender_counts = man_counts if gender == WOMAN_GENDER else woman_counts
            total = totals[gender]

            if total == 0:
                continue

            for word, count in counts_for_current_gender.items():
                tf = count / total
                documents_containing_current_term = 2 if word in another_gender_counts else 1
                idf = math.log(2 / documents_containing_current_term)
                term_score = tf * idf

                tf_idf_by_genders.append(
                    TfIdf(word=word,
                          score=term_score,
                          count=count,
                          gender=gender
                          )
                )

        return sorted(tf_idf_by_genders, key=lambda x: x.score, reverse=True)
