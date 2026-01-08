from typing import TypedDict


class GenderExtractorReturnType(TypedDict):
    """
    This type of dict represents the structure of return type for extractors. It is a type with two items: "label"
    (with type str) and "score" (type float).
    """
    label: str
    score: float
