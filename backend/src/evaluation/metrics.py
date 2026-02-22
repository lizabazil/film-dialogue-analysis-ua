from abc import ABC, abstractmethod

from schemas import ComparisonPair, EvalSegment
from collections import Counter


class TextMetricStrategy(ABC):
    """
    Interface for text comparison strategies.
    """

    @abstractmethod
    def calculate(self, ref_tokens: list[str], hyp_tokens: list[str]) -> float:
        pass


# specific strategies
class JaccardSimilarity(TextMetricStrategy):

    def calculate(self, ref_lemmas: list[str], hyp_lemmas: list[str]) -> float:
        """
        If the two documents are identical, Jaccard Similarity is 1. The Jaccard similarity score is 0 if there are
        no common words between two documents.
        Args:
            ref_lemmas:
            hyp_lemmas:

        Returns:

        """
        ref_set = set(ref_lemmas)
        hyp_set = set(hyp_lemmas)
        if not ref_set and not hyp_set:
            return 1.0

        intersection = ref_set.intersection(hyp_set)
        union = ref_set.union(hyp_set)

        # calculate jaccard similarity score
        return float(len(intersection)) / len(union)


# some other evaluators
class GenderEvaluator:

    def check_match(self, ref_segments: list[EvalSegment], hyp_segments: list[EvalSegment]) -> bool:
        reference_gender = self._get_majority_gender(ref_segments)
        hypothesis_gender = self._get_majority_gender(hyp_segments)
        return reference_gender == hypothesis_gender

    def _get_majority_gender(self, segments: list[EvalSegment]) -> str:
        if not segments:
            return "unknown"
        genders = [seg.gender for seg in segments]

        if not genders:
            return "unknown"

        counts = Counter(genders)
        # most_common(1) returns list like [('man', 5)]
        majority_gender, count = counts.most_common(1)[0]

        return majority_gender


# orchestrator (Context)
class MetricsEvaluator:

    def __init__(self):
        self.text_jaccard = JaccardSimilarity()
        self.gender_eval = GenderEvaluator()

    def evaluate(self, pair: ComparisonPair) -> None:
        """
        Writes evaluation results  to the corresponding field of the pair.
        Args:
            pair:

        Returns:

        """
        ref_lemmas = []
        for s in pair.ref_segments:
            ref_lemmas.extend(s.lemmas)

        hyp_lemmas = []
        for s in pair.hyp_segments:
            hyp_lemmas.extend(s.lemmas)

        text_score = self.text_jaccard.calculate(ref_lemmas, hyp_lemmas)
        pair.metrics["text_jaccard"] = text_score

        # evaluate gender precision
        gender_match = self.gender_eval.check_match(pair.ref_segments, pair.hyp_segments)
        pair.metrics["gender"] = gender_match

        return None
