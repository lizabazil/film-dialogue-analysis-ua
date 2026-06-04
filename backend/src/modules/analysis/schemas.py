from pydantic import BaseModel
from enum import Enum


class ReplicaType(str, Enum):  # about replica type
    REACTIVE = "reactive"  # 1-3 words
    STANDARD = "standard"  # 4-15 words
    EXTENDED = "extended"  # 16-40 words
    MONOLOGUE = "monologue"   # monologues  (>= 30 seconds long)


class PauseType(str, Enum):   # what is happening between replicas
    SMALL = "small"  # (0-200 ms)
    NORMAL_PAUSE = "normal_pause"  # max 1 second
    HESITATION = "hesitation"  # 1-2 seconds
    LONG_PAUSE = "long_pause"  # > 2 seconds


class SegmentPaceMetrics(BaseModel):  # info about segment type
    word_count: int
    duration_sec: float
    category: ReplicaType


class TurnTransition(BaseModel):  # about pause between two consequent segments
    duration_seconds: float
    pause_category: PauseType


class PaceTrendPoint(BaseModel):  # one sliding window
    timestamps_total_ms: float  # ms after the movie's start (at the end of the window)
    total_local_words: int
    silence_percentage: float  # percentage of silence in this window

    dominant_replica_type: ReplicaType | None
    dominant_pause_type: PauseType | None


class PaceGlobalAnalysis(BaseModel):
    total_monologues: int
    total_long_pauses: int
    total_instant_responses: int
    pace_graph: list[PaceTrendPoint]  # list of all windows


class BechdelTest(BaseModel):
    passed_bechdel_test: bool
    passed_points: int


class GenderBalance(BaseModel):
    woman_time_minutes: float
    man_time_minutes: float

    woman_replicas: int
    man_replicas: int
    avg_words_per_replica_woman: float
    avg_words_per_replica_man: float
    bechdel_test: BechdelTest


class MetaData(BaseModel):
    filename: str
    duration_minutes: int
    duration_seconds: int
    formatted_duration: str
    file_size_gb: float


class WordFrequency(BaseModel):
    word: str
    count: int


class PartOfSpeechUsage(BaseModel):
    gender: str
    part_of_speech: str
    percentage: float


class TfIdf(BaseModel):
    word: str
    score: float
    count: int
    gender: str


class SpeakerLexicon(BaseModel):
    top_man_lemmas: list[WordFrequency]
    top_woman_lemmas: list[WordFrequency]
    top_all_gender_lemmas: list[WordFrequency]
    top_nouns_all_genders: list[WordFrequency]
    top_verbs_all_genders: list[WordFrequency]
    top_adjectives_all_genders: list[WordFrequency]

    pos_usage_by_genders: list[PartOfSpeechUsage]
    tf_idf_by_genders: list[TfIdf]


class MovieAnalysisReport(BaseModel):
    gender_stats: GenderBalance
    metadata: MetaData
    speaker_lexicon: SpeakerLexicon
    pace_analysis: PaceGlobalAnalysis
