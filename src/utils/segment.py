from typing import Optional
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

    @property
    def total_ms_start(self) -> int:
        """
        Calculates the time of segment's start in  milliseconds.
        Returns:
            int: Time of start in milliseconds.
        """
        return (self.start_h * 3600000 +
                self.start_m * 60000 +
                self.start_s * 1000 +
                self.start_ms)

    @property
    def total_ms_end(self) -> int:
        """
        Calculates the time of segment's end in  milliseconds.
        Returns:
            int: Time of end in milliseconds.
        """
        return (self.end_h * 3600000 +
                self.end_m * 60000 +
                self.end_s * 1000 +
                self.end_ms)

    def add_nlp_data(self, new_data: list[TokenList] | None) -> None:
        """
        Appends a list of UDPipe TokenList objects to the existing NLP data.
        If the internal storage is currently uninitialized (None), a new list is created.
        If `new_data` is provided, it extends the internal list. If `new_data` is None, no changes are made to the
        object.

        Args:
            new_data (list[TokenList] | None): A list of processed token lists from UDPipe.
                If None is passed, the method simply returns without action.
        Returns:
            None
        """
        if not new_data:
            return None
        if self.nlp_data is None:
            self.nlp_data = []

        self.nlp_data.extend(new_data)
        return None

    def __repr__(self):
        return (f"SPEAKER_ID: {self.speaker_id}\n"
                f"START: {self.start_h}:{self.start_m}:{self.start_s}.{self.start_ms}\n"
                f"END: {self.end_h}:{self.end_m}:{self.end_s}.{self.end_ms}\n"
                f"SPEECH: {self.speech}\n"
                f"NLP_DATA: {self.nlp_data}\n")
