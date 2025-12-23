# TODO: implement
# this main file will be using all the methods for cleaning and formatting transcripts
from regex_cleaner import RegexCleaner
from llm_corrector import LLMCorrector


class TranscriptCleaner:
    """
    This class uses methods to properly clean transcripts (both rule-based approach and llm).
    """
    def __init__(self):
        self.regex_cleaner = RegexCleaner()
        self.llm_corrector = LLMCorrector()

    def clean_segments(self, segments: list) -> list:
        """
        Main method to clean segments using all methods.
        """


