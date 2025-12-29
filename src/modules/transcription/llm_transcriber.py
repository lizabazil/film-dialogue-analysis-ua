import google.generativeai as genai
from dotenv import load_dotenv
import os
from src.utils.time_utils import TimeUtils
from src.utils.audio_file_utils import AudioFileUtils
from src.utils.video_utils import VideoUtils
from google.api_core import exceptions
import time


def get_last_n_lines_from_response(response: str, last_n_lines: int = 30) -> str:
    lines = response.strip().split("\n")
    res = "\n".join(lines[-last_n_lines:])
    return res


def create_prompt_with_previous_context(previous_context: str = "") -> str:
    return f"""
    ТИ — ПРОФЕСІЙНИЙ ПЕРЕКЛАДАЧ ТА ТРАНСКРИБАТОР УКРАЇНСЬКИХ ФІЛЬМІВ.

    --- ВХІДНІ ДАНІ: КОНТЕКСТ ---
    Нижче наведено текст з попередньої частини фільму. 
    ВИКОРИСТОВУЙ ЙОГО ЛИШЕ ДЛЯ РОЗУМІННЯ КОНТЕКСТУ (хто говорить, про що, який рід вживати).
    НЕ ТРАНСКРИБУЙ І НЕ ПЕРЕКЛАДАЙ ЦЕЙ ТЕКСТ ЗНОВУ. ВІН ТУТ ТІЛЬКИ ДЛЯ ДОВІДКИ.

    <previous_context>
    {previous_context if previous_context else "Це початок фільму. Контексту немає."}
    </previous_context>

    --- ВХІДНІ ДАНІ: АУДІО ---
    Твоє завдання — працювати виключно з наданим АУДІО-файлом.

    --- ІНСТРУКЦІЇ ---
    1. Прослухай аудіо та транскрибуй мовлення.
    2. ОДРАЗУ перекладай транскрипцію українською мовою.
    3. Враховуй контекст з <previous_context> для правильного вибору роду, звертань та стилю.
    4. Формат виводу (суворий):
       [HH:MM:SS.ms - HH:MM:SS.ms] SPEAKER_XX: Текст репліки українською.
    5. Ідентифікація спікерів: Використовуй суворі мітки SPEAKER_01, SPEAKER_02 і так далі.

    --- ВАЖЛИВО ---
    - Ігноруй музику та шуми.
    - Якщо мова оригіналу не українська, перекладай літературно на українську мову.
    - НЕ виводь текст з розділу <previous_context> у фінальний результат. Починай лише з нових фраз з аудіо.
    """


class LLMTranscriber:
    """
    This class is responsible for sending requests to LLM in order to get a transcript of the movie (including
     timecodes for each replica).
     Uses chunked approach (the full audio file is split to the chunks with given length and overlap).
    """

    TimeInterval = tuple[float, float]  # type alias for simplifying structure

    def __init__(self, full_video_path: str, txt_file_path_for_transcript: str, model_name: str = "gemini-2.5-flash"):
        self.model_name = model_name
        self.full_video_path = full_video_path
        self.model = None
        # self.requirements_to_response = ('Вимоги до виводу:\n'
        #                         '1. Формат виводу: Поверни результат у вигляді простого тексту, де кожен рядок відповідає одному репліці у форматі: [HOUR:MINUTE:SECONDS.MS - HOUR:MINUTE:SECONDS.MS] SPEAKER_XX. Також виводь текст мовців.'
        #                         '3. Ідентифікація спікерів: Використовуй суворі мітки SPEAKER_01, SPEAKER_02 і так далі. Не намагайся вгадати імена чи ролі (наприклад, не пиши "Narrator" чи "Man").'
        #                         '4. Фільтрація: Ігноруй музику, звукові ефекти, тишу та немовленнєві звуки. Не включай їх у вивід.'
        #                         '5. Мова аудіо: українська.')
        self.requirements_to_response = (
            'Вимоги до виводу:\n'
            '1. Формат виводу: Поверни результат у вигляді простого тексту, де кожен рядок відповідає одній репліці у форматі: [HH:MM:SS.ms - HH:MM:SS.ms] SPEAKER_XX: Текст репліки.\n'
            '2. Ідентифікація спікерів: Використовуй суворі мітки SPEAKER_01, SPEAKER_02 і так далі.\n'
            '3. Фільтрація: Ігноруй музику, звукові ефекти, тишу та немовленнєві звуки.\n'
            '4. Переклад та мова: Цільова мова виводу — виключно УКРАЇНСЬКА. Аудіо може містити різні мови. Твоє завдання — розпізнати мовлення і ОДРАЗУ перекласти його українською мовою. Переклад має бути літературним та відповідати контексту фільму. Не пиши текст іноземною мовою, пиши лише український переклад.'
        )

        self.txt_file_path_for_transcript = txt_file_path_for_transcript
        self.chunk_length_in_min = 8  # the whole audio file will be split in chunks each being 8 minutes
        self.overlap_in_min = 1

        # here will be saved the full audio file of the given video
        self.full_audio_path = "../../../data/temporary_files/full_audio.mp3"
        AudioFileUtils.extract_audio_from_video(full_video_path, self.full_audio_path)

        self.temp_path_to_cut_audio_file = "../../../data/temporary_files/cut_audio.mp3"
        self.names_of_api_keys = ["GEMINI_API_KEY_1", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3", "GEMINI_API_KEY_4",
                                  "GEMINI_API_KEY_5"]
        self.next_key_index = 0

        load_dotenv()
        self._take_next_key()  # initialize model with the very first api key

        self.prev_response = ""

    def _take_next_key(self) -> None:
        """
        Configures API key from the list of given API keys.
        """
        api_key = os.getenv(self.names_of_api_keys[self.next_key_index])
        genai.configure(api_key=api_key)
        self.next_key_index += 1

        self.model = genai.GenerativeModel(self.model_name)
        return None

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

    def _send_safe_request(self, audio_file_path: str) -> str | None:
        """
        Sends request to the Gemini with given audio file and prepared text input.

        Args:
            audio_file_path (str): Path to the audio file, which needs to be transcribed.

        Returns:
            str | None: The output from the LLM model. Returns None in case of exception.
        """
        retries = 0
        max_retries = 3
        uploaded_file = None

        while retries < max_retries:
            try:
                if not uploaded_file:
                    uploaded_file = genai.upload_file(audio_file_path)

                while uploaded_file.state.name == "PROCESSING":
                    print("Uploading audio file...")
                    time.sleep(2)
                    uploaded_file = genai.get_file(uploaded_file.name)

                if uploaded_file.state.name == "FAILED":
                    raise ValueError("File upload failed on Google side...")

                response = self.model.generate_content(
                    [
                        uploaded_file,
                        #self.requirements_to_response,
                        create_prompt_with_previous_context(get_last_n_lines_from_response(self.prev_response, 30))
                    ]
                )
                text_response = response.text
                self.prev_response = text_response

                try:
                    uploaded_file.delete()
                except:
                    pass

                return text_response

            except exceptions.ResourceExhausted as e:
                print(f"Resource exhausted: {e}.\nWaiting 60 seconds in case this is RPM limit...")
                time.sleep(60)
                retries += 1

            except Exception as e:
                print(f"Exception while getting response: {e}")
                return None

        # probably reached the daily limit
        print("Probably max daily retries reached. Checking next API key...")
        try:
            if uploaded_file: uploaded_file.delete()
        except: pass

        if self.next_key_index < len(self.names_of_api_keys):
            self._take_next_key()
            return self._send_safe_request(audio_file_path)

        print("Unable to call API...")
        return None

    def _send_chunks_to_llm(self, chunks: list[TimeInterval]):
        """
        Sends chunks of audio with given length and writes transcription to the file.
        """
        for i, (start, end) in enumerate(chunks):
            AudioFileUtils.cut_audio_segment_in_ms(self.full_audio_path,
                                                   self.temp_path_to_cut_audio_file,
                                                   start_ms=start, end_ms=end)
            response = self._send_safe_request(self.temp_path_to_cut_audio_file)
            # TODO: convert to proper timecodes to match the full audio
            with open(self.txt_file_path_for_transcript, "a") as f:
                f.write(f"\n\n-- CHUNK {i} --\n")
                f.write(response)
        return None

    def write_full_transcript_to_the_file(self):
        hours, minutes, seconds = VideoUtils.get_duration_of_video(self.full_video_path)
        total_duration_in_ms = TimeUtils.convert_to_ms(hours, minutes, seconds, 0)
        chunks = self._get_chunk_intervals(total_duration_in_ms)
        # for debugging
        #for i, (s, e) in enumerate(chunks):
            #print(f'Chunk {i}: from {s} to {e} ms')
        #return
        self._send_chunks_to_llm(chunks)
        return None
