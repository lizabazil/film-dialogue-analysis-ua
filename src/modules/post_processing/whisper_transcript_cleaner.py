# will be applying various regex rules to clean up transcripts after Whisper model
import re
from src.utils.segment import Segment
import copy


class WhisperTranscriptCleaner:
    """
    This class contains rules for cleaning the Whisper's output.
    """
    MUSIC_PATTERN = re.compile(r"((Музика)\s+)|(Грає музика[.]?)")

    # pattern to match specific phrases (artifacts)
    EXCESSIVE_PHRASES_PATTERN = re.compile(r"(Субтитрувальниця Оля Шор)|(Дяку(ємо|ю) за перегляд!)|(Кінець брифінгу[.]?)|((найбільше)?\s*новини на Суспільному.(\s*Харків.)?)|(Звучить музика.)|(Редактор субтитров О.Голубкина Коректор А.Егорова)|(Увага на екран!)",
                                           re.IGNORECASE)

    # creating a new pattern for word "дякую" because this word is used in different contexts, so here won't be flag
    # 'ingnorecase'
    THANKS_PATTERN = re.compile(r"(Дякую[.!])")

    # pattern to match words/phrases repeated more than twice in a row
    REPEATED_PHRASE_PATTERN = re.compile(
            r'(([А-ЩЬЮЯҐЄІЇа-щьюяґєії]+\s+)*[А-ЩЬЮЯҐЄІЇа-щьюяґєії]+)(?:[,\.\!\s]*\1){3,}')

    # pattern to match sounds like "аааа", "ха-ха-ха", "б-б-б-б"
    STUTTER_PATTERN = re.compile(r'([А-ЩЬЮЯҐЄІЇа-щьюяґєії]{1,4})(?:[-]*\1){2,}', re.IGNORECASE)

    # pattern to match single letters repeated more than 3 times like "аааа", "бббб"
    ELONGATED_CHAR_PATTERN = re.compile(r'([А-ЩЬЮЯҐЄІЇа-щьюяґєії])\1{3,}', re.IGNORECASE)

    def __init__(self):
        pass

    def clean(self, segments: list[Segment]) -> list[Segment]:
        if not segments:
            return []

        cleaned_segments = self._remove_excessive_hallucinations(segments)
        cleaned_segments = self._clean_repetition_artifacts(cleaned_segments)
        return cleaned_segments

    def _remove_excessive_hallucinations(self, segments: list[Segment]) -> list[Segment]:
        """
        Filters out common hallucinated phrases and non-speech artifacts from the transcript segments.

        This method removes known Whisper artifacts such as:
        - Subtitler credits (e.g., "[Субтитрувальниця Оля...]").
        - Excessive gratitude phrases (e.g., "[Дякую за перегляд!]", "[Дякую]").
        - Music and applause tags.

        If a segment's text becomes empty after cleaning, that segment is excluded from the output.

        Args:
            segments (list[Segment]): The list of original transcript segments.

        Returns:
            list[Segment]: A new list of segments with sanitized speech text.
        """
        cleaned_segment_list = []

        for segment in segments:
            speech = segment.speech
            cleaned_speech = re.sub(self.EXCESSIVE_PHRASES_PATTERN, '', speech).strip()  # remove matched phrases
            cleaned_speech = re.sub(self.THANKS_PATTERN, '', cleaned_speech).strip()
            # there are also additional lines with word 'Музика', which should be removed
            cleaned_speech = self._remove_music_tags(cleaned_speech)

            if cleaned_speech:
                new_segment = copy.copy(segment)
                new_segment.speech = cleaned_speech
                cleaned_segment_list.append(new_segment)

        return cleaned_segment_list

    def _remove_music_tags(self, text):
        """
        Delete the word 'Музика' from the text, if it is present alone or not in the sentence.
        Args:
            text (str): The input text.
        Returns:
            cleaned_text (str): The cleaned text without the word 'Музика'.
        """
        # remove 'Музика' if it is the only word
        if text.strip() == 'Музика':
            return ''
        cleaned_text = re.sub(self.MUSIC_PATTERN, '', text).strip()
        return cleaned_text

    def _clean_repetition_artifacts(self, segments: list[Segment]) -> list[Segment]:
        """
        Detects and normalizes repetitive speech patterns in the transcript segments.

        This method applies regex-based cleaning to handle three types of Whisper artifacts:
        1. Phrase looping (repeating words/phrases multiple times).
        2. Stuttering (e.g., "b-b-but").
        3. Character elongation (e.g., "aaaaah").

        The repetitions are reduced to a single occurrence (e.g., "no no no" -> "no").
        Segments that become empty after cleaning are excluded from the result.

        Args:
            segments (list[Segment]): The list of original transcript segments.

        Returns:
            list[Segment]: A new list of segments with normalized speech text.
        """
        cleaned_list = []

        for segment in segments:
            text = segment.speech
            cleaned_speech = self.REPEATED_PHRASE_PATTERN.sub(r'\1', text).strip()
            cleaned_speech = self.STUTTER_PATTERN.sub(r'\1', cleaned_speech).strip()
            cleaned_speech = self.ELONGATED_CHAR_PATTERN.sub(r'\1', cleaned_speech).strip()

            if cleaned_speech:
                new_segment = copy.copy(segment)
                new_segment.speech = cleaned_speech
                cleaned_list.append(new_segment)

        return cleaned_list
