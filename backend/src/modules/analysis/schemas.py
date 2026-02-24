from pydantic import BaseModel


class GenderBalance(BaseModel):
    woman_time_minutes: float
    man_time_minutes: float

    woman_replicas: int
    man_replicas: int
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
