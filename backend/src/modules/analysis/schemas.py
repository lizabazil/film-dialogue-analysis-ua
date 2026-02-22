from pydantic import BaseModel


class GenderBalance(BaseModel):
    woman_time_minutes: float
    man_time_minutes: float
    #man_time_ms: int
    #woman_time_ms: int
    #man_word_count: int
    #woman_word_count: int


class MetaData(BaseModel):
    filename: str
    duration_minutes: int
    formatted_duration: str
    file_size_gb: float


class MovieAnalysisReport(BaseModel):
    gender_stats: GenderBalance
    metadata: MetaData
    #top_keywords: list[dict[str, int]]
