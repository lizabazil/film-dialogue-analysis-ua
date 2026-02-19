from pydantic import BaseModel


class GenderBalance(BaseModel):
    man_time_ms: int
    woman_time_ms: int
    man_word_count: int
    woman_word_count: int


class MovieAnalysisReport(BaseModel):
    gender_stats: GenderBalance
    top_keywords: list[dict[str, int]]
