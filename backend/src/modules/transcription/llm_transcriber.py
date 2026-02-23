import re

import google.generativeai as genai
from dotenv import load_dotenv
import os
from src.utils.time_utils import TimeUtils
from src.utils.audio_file_utils import AudioFileUtils
from src.utils.video_utils import VideoUtils
from src.utils.file_utils import FileUtils
from google.api_core import exceptions
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import time
import secrets
import string
from datetime import datetime
from pathlib import Path
from collections import Counter


def get_last_n_lines_from_response(response: str, last_n_lines: int = 30) -> str:
    lines = response.strip().split("\n")
    res = "\n".join(lines[-last_n_lines:])
    return res


def create_prompt_with_previous_context(previous_context: str = "") -> str:
    """
    To create strict prompt with context from the previous subscription.
    This approach will not be used in the final implementation for LLM transcriber, since it does not give
    better results and sometimes may even lead to the model confusion.

    Args:
        previous_context (str):
    Returns:
        str: The ready prompt with inserted previous context.
    """
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
    RESPONSE_STRUCTURE_PATTERN_WITH_GENDER = re.compile(r"\[\d{1,2}:\d{1,2}(:\d{1,2})?[.:]\d{1,3}\s-\s\d{1,2}:\d{1,2}(?::\d{1,2})?[.:]\d{1,3}\]\s+SPEAKER_\w+\s*(\([FM]\)):\s*.*")
    RESPONSE_STRUCTURE_PATTERN_WITHOUT_GENDER = re.compile(r"\[\d{1,2}:\d{2}(:\d{2})?[.:]\d{1,3}\s-\s\d{1,2}:\d{2}(?::\d{2})?[.:]\d{1,3}\]\s+SPEAKER_\w+\s*:\s*.*")

    def __init__(self, config: dict):
        self.model_name = config["llm_transcriber"]["model_name"]
        self.model = None
        # self.requirements_to_response = (
        #     'Контекст: Це запит для технічної транскрипції та лінгвістичного аналізу медіа-файлу. Вміст може містити розмовну лексику, яку необхідно транскрибувати дослівно для точності документації. Будь ласка, ігноруй тональність і зосередься на точності тексту.'
        #     'Вимоги до виводу:\n'
        #     '1. Формат виводу: Поверни результат у вигляді простого тексту. Кожен рядок — одна репліка.\n'
        #     '   Формат: [HH:MM:SS.ms - HH:MM:SS.ms] SPEAKER_XX: Текст репліки.\n'
        #     '   ВАЖЛИВО: Використовуй ВІДНОСНИЙ час аудіофайлу. Тобто початок аудіо — це завжди 00:00:00.000. '
        #     'Не намагайся обчислювати реальний час фільму.\n'
        #     '2. Ідентифікація спікерів: Використовуй суворі мітки SPEAKER_01, SPEAKER_02 і так далі.\n'
        #     '3. Фільтрація: Ігноруй музику, звукові ефекти, тишу та немовленнєві звуки.\n'
        #     '4. Точність часу: Таймкод початку — момент ПЕРШОГО звуку голосу. Таймкод кінця — момент ОСТАННЬОГО звуку. '
        #     'Обов\'язково вказуй мілісекунди.\n'
        #     '5. Переклад: Цільова мова — виключно УКРАЇНСЬКА. Якщо наявна інша мова - перекладай літературно, одразу з аудіо. '
        #     'Не пиши оригінальний текст.')
        self.requirements_to_response = (
            'Контекст: Це запит для технічної транскрипції, лінгвістичного аналізу та ідентифікації статі мовців. '
            'Вміст може містити розмовну лексику, яку необхідно транскрибувати дослівно. Ігноруй тональність, зосередься на точності.\n'
            'Вимоги до виводу:\n'
            '1. Формат виводу: Простий текст, кожен рядок — одна репліка.\n'
            '   Формат: [HH:MM:SS.ms - HH:MM:SS.ms] SPEAKER_XX (GENDER): Текст репліки.\n'
            '   Де GENDER — це: M (чоловік) або F (жінка)\n'
            '   ВАЖЛИВО: Використовуй ВІДНОСНИЙ час аудіофайлу (початок = 00:00:00.000).\n'
            '2. Ідентифікація спікерів та статі: Використовуй суворі мітки SPEAKER_01, SPEAKER_02. '
            'Стать визначай за голосом.\n'
            '3. Точність часу: Таймкоди мають включати мілісекунди (ms).\n'
            '4. Переклад: Цільова мова — УКРАЇНСЬКА. Якщо звучить інша мова - перекладай літературно, без оригіналу.\n'
            '5. ЗАБОРОНА ГАЛЮЦИНАЦІЙ: Категорично заборонено додумувати слова з фонового шуму.'
            'Не інтерпретуй подих, кроки чи вітер як вигуки.\n'
            '6. Фільтрація та Тиша: > * НЕ ТРАНСКРИБУЙ музику, шум, подих або тишу як окремі репліки всередині діалогу.'
            'ЯКЩО В УСЬОМУ ФАЙЛІ ВІДСУТНЄ МОВЛЕННЯ: Видай лише один рядок:'
            '[00:00.000 - 07:59.999] SPEAKER_100 (U): [no speech]'
        )

        self._txt_file_path_for_transcript = None
        # the whole audio file will be split in chunks each being 8 minutes
        self.chunk_length_in_min = config.get("llm_transcriber", {}).get("chunk_length_in_min", 8)
        self.overlap_in_min = config.get("llm_transcriber", {}).get("overlap_in_min", 1)

        # here will be saved the full audio file of the given video
        self.full_audio_path = self._generate_path_with_given_main_name("full_audio_for_transciber")

        self.temp_path_to_cut_audio_file = self._generate_path_with_given_main_name("cut_audio_for_transcriber")
        self.names_of_api_keys = config["llm_transcriber"]["api_keys_config"]["env_variables_names"]
        self.next_key_index = 0

        load_dotenv()
        self._take_next_key()  # initialize model with the very first api key

        self.prev_response = ""

    def _generate_path_with_given_main_name(self, main_name: str, ds_directory: str = "../../../data/temporary_files"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(6))
        directory = Path(ds_directory)
        directory.mkdir(parents=True, exist_ok=True)
        return str(directory / f"{main_name}_{timestamp}_{random_suffix}.mp3")

    def _take_next_key(self) -> None:
        """
        Configures API key from the list of given API keys.
        """
        key_name = self.names_of_api_keys[self.next_key_index]
        api_key = os.getenv(key_name)
        genai.configure(api_key=api_key)
        self.next_key_index += 1

        self.model = genai.GenerativeModel(self.model_name)
        print(f"Changed key. New key is {key_name}")
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
        Sends request to the Gemini with one given audio file (one chunk) and prepared text input.

        Args:
            audio_file_path (str): Path to the audio file, which needs to be transcribed.

        Returns:
            str | None: The output from the LLM model. Returns None in case of exception.
        """
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }

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

                response = self.model.generate_content([uploaded_file, self.requirements_to_response],
                                                       safety_settings=safety_settings
                                                       )
                text_response = response.text
                self.prev_response = text_response
                self._safe_delete_file(uploaded_file)
                return text_response

            except exceptions.ResourceExhausted as e:
                print(f"Resource exhausted: {e}.\nWaiting 60 seconds in case this is RPM limit...")
                time.sleep(60)
                retries += 1
            except Exception as e:
                print(f"Exception while getting response: {e}")
                retries += 1
                time.sleep(2)

        # probably reached the daily limit
        print("Probably max daily retries reached. Checking next API key...")
        self._safe_delete_file(uploaded_file)

        if self.next_key_index < len(self.names_of_api_keys):
            self._take_next_key()
            return self._send_safe_request(audio_file_path)

        print("Unable to call API...")
        return None

    def _safe_delete_file(self, file_object):
        try:
            if file_object:
                file_object.delete()
        except Exception as e:
            print(f"Cannot delete the file: {e}")

    def _send_chunks_to_llm(self, chunks: list[TimeInterval]) -> None:
        """
        Sends chunks of audio with given length to the LLM and writes transcription to the output file.
        Args:
            chunks (list[TimeInterval]): Chunks which consist of start and end timecodes (relatively to the whole movie).
        Returns:
            None
        """
        for i, (start, end) in enumerate(chunks):
            AudioFileUtils.cut_audio_segment_in_ms(self.full_audio_path,
                                                   self.temp_path_to_cut_audio_file,
                                                   start_ms=start, end_ms=end)

            response = None
            # because llm may not return anything because of so-called copyright material, that's why we are trying to
            # get response until we get it
            while response is None:
                response = self._send_safe_request(self.temp_path_to_cut_audio_file)

                if response is None:  # in case with exception, the model returns None
                    print(f"Error for chunk {i}. Trying again.")
                    continue

                print(f"Got response from llm for chunk {i}") if response is not None else print(f"Didn't get "
                                                                                                 f"response from llm "
                                                                                                 f"for chunk {i}")
                # check for hallucinations
                is_last_chunk = (i == len(chunks) - 1)
                is_hallucinating, response = self._is_hallucinating(response, chunk_num=i, is_last_chunk=is_last_chunk)
                if is_hallucinating:
                    response = None

            with open(self._txt_file_path_for_transcript, "a") as f:
                f.write(f"-- CHUNK {i} --\n")
                f.write(response)
                f.write("\n\n")

        # delete temporary files with audio to release space
        FileUtils.delete_file(self.full_audio_path)
        FileUtils.delete_file(self.temp_path_to_cut_audio_file)
        return None

    def write_full_transcript_to_the_file(self, full_video_path: str, txt_file_path_for_transcript: str) -> None:
        """
        Method for getting transcript of the whole audio.
        Firstly, this method detect the duration of the movie. Secondly, it splits the whole movie into the chunks of
        a set length.
        Lastly, this method writes the final transcript to the given output file.

        Returns:
            None
        """
        self.set_txt_file_path_for_transcript(txt_file_path_for_transcript)

        # delete file in which will be transcript from LLM (this file may be already present, so it is done to avoid
        # mixing data)
        FileUtils.delete_file(self._txt_file_path_for_transcript)

        AudioFileUtils.extract_audio_from_video(full_video_path, self.full_audio_path)
        hours, minutes, seconds = VideoUtils.get_duration_of_video(full_video_path)
        total_duration_in_ms = TimeUtils.convert_to_ms(hours, minutes, seconds, 0)
        chunks = self._get_chunk_intervals(total_duration_in_ms)
        print(f"Number of chunks: {len(chunks)}")
        self._send_chunks_to_llm(chunks)
        return None

    def set_txt_file_path_for_transcript(self, value: str):
        """
        Setter for output transcript file path.

        Args:
             value (str): New path to be set.
        Returns:
            None
        """
        self._txt_file_path_for_transcript = value

    def _is_hallucinating(self, response: str, threshold: float = 0.4, chunk_num: int = None,
                          is_last_chunk: bool = False) -> tuple[bool, str]:
        default_no_speech_response = "[00:00:00.000 - 00:01:00.000] SPEAKER_100 (U): [no sound]"
        if not response or not response.strip():
            return True, response

        lines = [l for l in response.split("\n") if l.strip()]

        meta_keywords = ["музика", "music", "тиша", "no speech", "no_speech", "background", "noise", "стогін", "вигук"]
        if len(lines) <= 2:  # max 2 lines in the whole chunk
            response_lower = response.lower()
            if any(key in response_lower for key in meta_keywords):  # basically, no speech in the whole chunk
                print(f"Accepted meta-response (likely without replicas) in chunk {chunk_num}: {response}")
                return False, default_no_speech_response

        # 1. structure check
        for line in lines:
            if not re.match(self.RESPONSE_STRUCTURE_PATTERN_WITH_GENDER, line):
                print(f"Hallucinating (structure) in chunk {chunk_num}: {line}")
                return True, response
            if not self._is_timecode_valid(line):
                print(f"Hallucinating (timecodes are incorrect) in chunk {chunk_num}: {line}")

        speech_content = [line.rsplit(":", 1)[-1].strip().lower() for line in lines]
        if not speech_content:
            return False, response
        if len(speech_content) < 3:  # less than three replicas in the whole chunk
            return False, response

        # 6. internal cycle loop
        for line_text in speech_content:
            if len(line_text) > 50:  # pretty long speech text
                char_uniqueness = len(set(line_text)) / len(line_text)
                if char_uniqueness < 0.1:
                    print(f"Hallucinating (internal char loop in speech text in chunk {chunk_num}: {line_text}")
                    return True, response

                # check for extremely long words without spaces
                longest_word_len = max((len(w) for w in line_text.split()), default=0)
                if longest_word_len > 50:  # word with more than 50 symbols is considered a hallucination
                    print(f"Hallucinating (infinite loop) in chunk: {chunk_num}: {line_text}")
                    return True, response

        current_threshold = 0.85 if is_last_chunk else threshold
        min_unique_ratio = 0.05 if is_last_chunk else 0.25
        max_consecutive = 50 if is_last_chunk else 10

        # 2. check for cycle pairs
        if len(speech_content) >= 4:
            # create pairs like this: [(L1, L2), (L2, L3), (L3, L4)...]
            line_pairs = list(zip(speech_content, speech_content[1:]))
            pair_counts = Counter(line_pairs)

            if pair_counts:
                most_common_pair, pair_count = pair_counts.most_common(1)[0]
                pair_ratio = (pair_count * 2) / len(speech_content)

                pair_limit = 0.95 if is_last_chunk else 0.7
                if pair_ratio > pair_limit and pair_count >= 4:
                    print(f"Hallucinating (cycle loop) in chunk {chunk_num}: {most_common_pair}")
                    return True, response

        # 3. check if enough uniqueness in the whole chunk
        if len(speech_content) > 6:
            unique_ratio = len(set(speech_content)) / len(speech_content)
            if unique_ratio < min_unique_ratio:
                print(f"Hallucinating (low uniqueness) in chunk {chunk_num}: ratio {unique_ratio}")
                return True, response

        # 4. check consecutive repetitions (A-A-A-A)
        consecutive_count = 1
        for i in range(1, len(speech_content)):
            if speech_content[i] == speech_content[i - 1] and len(speech_content[i]) > 0:
                consecutive_count += 1
                if consecutive_count >= max_consecutive:  # at least 10 the same replicas
                    print(f"Hallucinating (consecutive) in chunk {chunk_num}: '{speech_content[i]}'")
                    return True, response
            else:
                consecutive_count = 1

        # 5. whether any replica appears very often in the whole chunk (this may indicate that the model has
        # hallucinated)
        line_counts = Counter(speech_content)
        most_common_line, count = line_counts.most_common(1)[0]
        if count / len(speech_content) > current_threshold:
            print(f"Hallucinating (global repetition) in chunk {chunk_num}: {most_common_line}")
            return True, response

        return False, response

    def _is_timecode_valid(self, line: str) -> bool:
        time_match = re.search(r"\[([\d:.]+) - ([\d:.]+)\]", line)

        if not time_match:
            return False  # the line is in the wrong format

        start_str, end_str = time_match.groups()

        def timecode_to_ms(timecode_str: str) -> int:
            timecode_str = timecode_str.replace('.', ':')
            parts = list(map(int, timecode_str.split(':')))

            parts = parts[::-1]

            ms = parts[0]
            seconds = parts[1] if len(parts) > 1 else 0
            minutes = parts[2] if len(parts) > 2 else 0
            hour = parts[3] if len(parts) > 3 else 0

            return ms + (seconds * 1000) + (minutes * 60000) + (hour * 3600000)

        try:
            start_ms = timecode_to_ms(start_str)
            end_ms = timecode_to_ms(end_str)

            return end_ms >= start_ms
        except Exception:
            return False
