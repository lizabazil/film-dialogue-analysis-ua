from typing import Optional
from conllu import TokenList


class Segment:
    """
    Class to represent segment. It contains such information as speaker_id, start and end timecode for speech,
    speech.
    """
    def __init__(self, speaker_id: str = "unknown",
                 start_h: int = 0,
                 start_m: int = 0,
                 start_s: int = 0,
                 start_ms: int = 0,
                 end_h: int = 0,
                 end_m: int = 0,
                 end_s: int = 0,
                 end_ms: int = 0,
                 speech: str = "",
                 gender: str = "unknown"):
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

    def set_start_time(self, hour: int, minute: int, second: int, millisecond: int) -> None:
        self.start_h = hour
        self.start_m = minute
        self.start_s = second
        self.start_ms = millisecond
        return None

    def set_end_time(self, hour: int, minute: int, second: int, millisecond: int) -> None:
        self.end_h = hour
        self.end_m = minute
        self.end_s = second
        self.end_ms = millisecond
        return None

    def to_dict(self) -> dict:
        return {
            "speaker_id": self.speaker_id,
            "total_ms_start": self.total_ms_start,
            "total_ms_end": self.total_ms_end,
            "start_h": self.start_h,
            "start_m": self.start_m,
            "start_s": self.start_s,
            "start_ms": self.start_ms,
            "end_h": self.end_h,
            "end_m": self.end_m,
            "end_s": self.end_s,
            "end_ms": self.end_ms,
            "speech": self.speech,
            "gender": self.gender
        }


    def __repr__(self):
        return (f"SPEAKER_ID: {self.speaker_id}\n"
                f"START: {self.start_h}:{self.start_m}:{self.start_s}.{self.start_ms}\n"
                f"END: {self.end_h}:{self.end_m}:{self.end_s}.{self.end_ms}\n"
                f"SPEECH: {self.speech}\n"
                f"NLP_DATA: {self.nlp_data}\n")
