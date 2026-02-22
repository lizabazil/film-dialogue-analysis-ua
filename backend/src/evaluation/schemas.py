from dataclasses import dataclass, field


@dataclass
class EvalSegment:  # bigger segment with: start, end, text, lemmas, speaker_id, gender
    start_ms: int = 0
    end_ms: int = 0
    speech: str = ""
    speaker_id: str = ""
    gender: str = ""
    lemmas: list[str] = field(default_factory=list)

    def set_start_time(self, h: int, m: int, s: int, ms: int):
        self.start_ms = (h * 3600000) + (m * 60000) + (s * 1000) + ms

    def set_end_time(self, h: int, m: int, s: int, ms: int):
        self.end_ms = (h * 3600000) + (m * 60000) + (s * 1000) + ms


@dataclass
class ComparisonPair:  # pair: segment from etalon (reference) (or a few) + segment form LLM
    ref_segments: list[EvalSegment]
    hyp_segments: list[EvalSegment]

    metrics: dict = field(default_factory=dict)   # here will be evaluation results

    # text metrics for this pair
    # text_similarity: float = None  # Jaccard or WER
    # ref_text_joined: str = ""
    # hyp_text_joined: str = ""
    #
    # gender_match: bool = False      # is gender the same
    # ref_gender: str = "unknown"
    # hyp_gender: str = "unknown"


@dataclass
class FinalEvaluationReport:
    avg_jaccard: float
    gender_accuracy: float

    pairs: list[ComparisonPair]
    total_pairs: int
    pairs_data: list[dict] = field(default_factory=list)
