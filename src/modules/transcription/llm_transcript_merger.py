import re


class LLMTranscriptMerger:
    """
    This class is used for reading and parsing output (full transcription for a single audio/movie) from the LLM.
    It creates new text file with cleaned transcript and proper timecodes.
    """
    TimeCode = tuple[int, int, int]  # minute, second, millisecond

    def __init__(self):
        pass

    def _set_to_proper_timecode(self,  chunk_num: int):
        """
        Changes the time of replica's timecode, respectively to the whole audio.
        """
        pass

    def parse_timecode(self, timecode: str) -> TimeCode:
        """
        Parses timecode to proper structure (which has type integer).
        LLM's output may contain timecodes in a bit different formats.
        """
        # remove all non-decimal and not :. symbols
        timecode = re.sub("[^0-9:.]", "", timecode)
        parts = re.split(r"[:.]", timecode)
        minute, second, ms = int(parts[-3]), int(parts[-2]), int(parts[-1])
        return minute, second, ms

