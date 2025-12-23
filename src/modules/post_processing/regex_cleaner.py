# TODO: implement regex cleaner module
# will be applying various regex rules to clean up transcripts
import re


class RegexCleaner:
    """
    This class contains rules for cleaning the Whisper's output.
    """
    def clean_from_whisper_exsessive_lines(self, transcript_list: list) -> list:
        """
        Remove phrases from Whisper, which is not part of the actual transcript.
        Those are phrases like "[Субтитрувальниця Оля Шор], [Дякую!], [Дякую за перегляд!], [Дякую.], [Кінець брифінгу]
        Args:
            transcript_list (list of dict): List of transcript entries, each entry is a dict with keys 'speaker', 'timecode_start', 'timecode_end', 'text'.
        Returns:
            cleaned_transcript_list (list of dict): Cleaned list of transcript entries.
            """
        cleaned_transcript_list = []
        pattern = re.compile(
            r'(Субтитрувальниця Оля Шор)|(Дяку(ємо|ю) за перегляд!)|(Кінець брифінгу[.]?)|((найбільше)?\s*новини на Суспільному.(\s*Харків.)?)|(Звучить музика.)|(Редактор субтитров О.Голубкина Коректор А.Егорова)|(Увага на екран!)',
            re.IGNORECASE)  # pattern to match specific phrases
        # creating a new pattern because this word is used in different contexts, so here won't be flag 'ingnorecase'
        pattern_thanks = re.compile(r'(Дякую[.!])')

        for replica in transcript_list:
            text = replica['text']
            cleaned_text = re.sub(pattern, '', text).strip()  # remove matched phrases
            cleaned_text = re.sub(pattern_thanks, '', cleaned_text).strip()
            # there are also additional lines with word 'Музика', which should be removed
            cleaned_text = delete_word_music(cleaned_text)

            if cleaned_text:
                cleaned_transcript_list.append({
                    'speaker': replica['speaker'],
                    'timecode_start': replica['timecode_start'],
                    'timecode_end': replica['timecode_end'],
                    'text': cleaned_text
                })

        return cleaned_transcript_list
