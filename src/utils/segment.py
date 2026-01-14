from typing import Optional, Any
from conllu import TokenList


class Segment:
    """
    Class to represent segment. It contains such information as speaker_id, start and end timecode for speech,
    speech.
    """
    def __init__(self, speaker_id: str, start_h: int, start_m: int, start_s: int, start_ms: int,
                 end_h: int, end_m: int, end_s: int, end_ms: int, speech: str, gender: str = "unknown"):
        self.speaker_id = speaker_id
        self.start_h = start_h  # hour
        self.start_m = start_m  # minute
        self.start_s = start_s   # second
        self.start_ms = start_ms  # millisecond
        self.end_h = end_h
        self.end_m = end_m
        self.end_s = end_s
        self.end_ms = end_ms
        self.speech = speech
        self.gender = gender   # 'female', 'male' or 'unknown'
        self.nlp_data: Optional[list[TokenList]] = None

