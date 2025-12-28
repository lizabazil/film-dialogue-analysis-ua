import google.generativeai as genai
from dotenv import load_dotenv
import os
from src.utils.time_utils import TimeUtils


class LLMTranscriber:
    """
    This class is responsible for sending requests to LLM in order to get a transcript of the movie (including
     timecodes for each replica).
     Uses chunked approach (the full audio file is split to the chunks with given length and overlap).
    """

    TimeInterval = tuple[float, float]  # type alias for simplifying structure

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        # self.requirements_to_response = ('Вимоги до виводу:\n'
        #                         '1. Формат виводу: Поверни результат у вигляді простого тексту, де кожен рядок відповідає одному репліці у форматі: [HOUR:MINUTE:SECONDS.MS - HOUR:MINUTE:SECONDS.MS] SPEAKER_XX. Також виводь текст мовців.'
        #                         '3. Ідентифікація спікерів: Використовуй суворі мітки SPEAKER_01, SPEAKER_02 і так далі. Не намагайся вгадати імена чи ролі (наприклад, не пиши "Narrator" чи "Man").'
        #                         '4. Фільтрація: Ігноруй музику, звукові ефекти, тишу та немовленнєві звуки. Не включай їх у вивід.'
        #                         '5. Мова аудіо: українська.')
        self.requirements_to_response = (
            'Вимоги до виводу:\n'
            '1. Формат виводу: Поверни результат у вигляді простого тексту, де кожен рядок відповідає одній репліці у форматі: [HOUR:MINUTE:SECONDS.MS - HOUR:MINUTE:SECONDS.MS] SPEAKER_XX: Текст репліки.\n'
            '2. Ідентифікація спікерів: Використовуй суворі мітки SPEAKER_01, SPEAKER_02 і так далі.\n'
            '3. Фільтрація: Ігноруй музику, звукові ефекти, тишу та немовленнєві звуки.\n'
            '4. Переклад та мова: Цільова мова виводу — виключно УКРАЇНСЬКА. Аудіо може містити різні мови. Твоє завдання — розпізнати мовлення і ОДРАЗУ перекласти його українською мовою. Переклад має бути літературним та відповідати контексту фільму. Не пиши текст іноземною мовою, пиши лише український переклад.'
        )

        self.chunk_length_in_min = 8  # the whole audio file will be split in chunks each being 8 minutes
        self.overlap_in_min = 1
        self.temp_path_to_cut_audio_file = "../../../data/temporary_files/cut_audio.mp3"

        load_dotenv()
        names_of_api_keys = ["GEMINI_API_KEY", "GEMINI_API_KEY_SECOND"]
        api_key = os.getenv("GEMINI_API_KEY")
        genai.configure(api_key=api_key)

    def _get_chunk_intervals(self, total_duration_ms: float) -> list[TimeInterval]:
        """
        Args:
            total_duration_ms (float): Total duration of the whole audio file.

        Returns:
            list[tuple[float, float]]: The list of tuples, where each tuple contains start and end time of chunks.
        """
        chunk_len_ms = TimeUtils.convert_to_ms(0, self.chunk_length_in_min, 0, 0)
        overlap_ms = TimeUtils.convert_to_ms(0, self.overlap_in_min, 0, 0)

        step_ms = chunk_len_ms - overlap_ms
        chunks = []

        current_start = 0.0
        while current_start < total_duration_ms:
            current_end = current_start + chunk_len_ms

            # if our last chunk will be shorter due to the audio length
            if current_end > total_duration_ms:
                current_end = total_duration_ms

            chunks.append((current_start, current_end))
            # if reached end of the audio
            if current_end == total_duration_ms:
                break

            current_start += step_ms

        return chunks

    def send_chunks_to_llm(self, chunks: list[TimeInterval]):
        pass


