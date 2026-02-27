from pydantic import BaseModel
from enum import Enum


class ReplicaType(str, Enum):  # about replica type (how short/long it is)
    REACTIVE = "reactive"  # very short replicas (1-3 words only)
    STANDARD = "standard"  # normal replicas (4-15 words)
    EXTENDED = "extended"  # extended replicas (16-40)
    MONOLOGUE = "monologue"   # long monologues  (>= 40 words or >= 30 seconds long)  # TODO: probably delete about monologue duration


class PauseType(str, Enum):   # what is happening between replicas
    SMALL = "small"  # very quick reaction to the prev segment (0-200 ms)
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


class PaceTrendPoint(BaseModel):  # for one sliding window
    timestamps_total_ms: float  # ms after the movie's start
    total_local_words: int
    silence_percentage: float  # percentage of silence in this window  (0-100)

    dominant_replica_type: ReplicaType  # which type of replicas was the most common in this window
    dominant_pause_type: TurnTransition


class PaceGlobalAnalysis(BaseModel):
    #result_pace_label: str  # slow, normal, dynamic

    total_monologues: int
    total_long_pauses: int
    total_instant_responses: int

    pace_graph: list[PaceTrendPoint]  # list of all windows


class BechdelTest(BaseModel):
    passed_bechdel_test: bool
    passed_points: int  # how many points were passed for this test (1, 2, or 3)


class GenderBalance(BaseModel):
    woman_time_minutes: float
    man_time_minutes: float

    woman_replicas: int
    man_replicas: int
    avg_words_per_replica_woman: float
    avg_words_per_replica_man: float
    bechdel_test: BechdelTest  # info about Bechdel test
    #man_time_ms: int
    #woman_time_ms: int
    #man_word_count: int
    #woman_word_count: int


class MetaData(BaseModel):
    filename: str
    duration_minutes: int
    formatted_duration: str
    file_size_gb: float


class WordFrequency(BaseModel):
    word: str
    count: int


class SpeakerLexicon(BaseModel):
    top_man_lemmas: list[WordFrequency]
    top_woman_lemmas: list[WordFrequency]
    top_all_gender_lemmas: list[WordFrequency]
    top_nouns_all_genders: list[WordFrequency]
    top_verbs_all_genders: list[WordFrequency]
    top_adjectives_all_genders: list[WordFrequency]


class MovieAnalysisReport(BaseModel):
    gender_stats: GenderBalance
    metadata: MetaData
    speaker_lexicon: SpeakerLexicon
