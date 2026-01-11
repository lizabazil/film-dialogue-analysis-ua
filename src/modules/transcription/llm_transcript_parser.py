import re
from src.utils.time_utils import TimeUtils
from src.utils.file_utils import FileUtils
import os
from itertools import groupby


class LLMTranscriptParser:
    """
    This class is used for reading and parsing output (full transcription for a single audio/movie) from the LLM.
    It creates new text file with cleaned transcript and proper timecodes.
    """
    SPEAKER_PATTERN = re.compile(r"(SPEAKER.*?):")
    SPEECH_PATTERN = re.compile(r"SPEAKER_\w+:\s+(.*)")
    TIMECODE_PATTERN = re.compile(r"\[(.*?)\s*-\s*(.*?)]")
    SPEAKER_PERSONAL_NUM_PATTERN = re.compile(r"SPEAKER_(\d+)")

    TimeCode = tuple[int, int, int, int]  # hour, minute, second, millisecond

    def __init__(self, config: dict):
        self.chunk_length_in_min = config.get("llm_transcriber", {}).get("chunk_length_in_min", 0)
        self.overlap_in_min = config.get("llm_transcriber", {}).get("overlap_in_min", 0)
        self.step_ms = (TimeUtils.convert_to_ms(0, self.chunk_length_in_min, 0, 0) -
                        TimeUtils.convert_to_ms(0, self.overlap_in_min, 0, 0))

    def _set_to_proper_timecode(self, chunk_num: int, timecode: TimeCode) -> TimeCode:
        """
        Changes the time of replica's timecode, respectively to the whole audio.
        """
        # L = 8 minutes * chunk_number -> proper start of the chunk
        # R = then timecode + L
        eight_min_in_ms = TimeUtils.convert_to_ms(0, self.chunk_length_in_min, 0, 0)
        h, m, s, ms = timecode
        timecode_in_ms = TimeUtils.convert_to_ms(h, m, s, ms)
        chunk_start_in_ms = eight_min_in_ms * chunk_num  # L
        res_in_ms = timecode_in_ms + chunk_start_in_ms  # R
        h, m, s, ms = TimeUtils.convert_ms_to_normal(res_in_ms)
        return h, m, s, ms

    def _parse_timecode(self, timecode: str) -> TimeCode:
        """
        This method is made to be used with only those timecodes, which are provided by LLM, because the hour in each
        timecode is set to 0.
        Parses timecode to proper structure (which has type integer).

        Args:
            timecode (str): Timecode in raw format (00:05:42.752, 01:51:309 etc.)
        Returns:
            TimeCode: Proper parsed timecode.
        """
        # remove all non-decimal and not :. symbols
        timecode = re.sub("[^0-9:.]", "", timecode)
        parts = re.split(r"[:.]", timecode)
        hour, minute, second, ms = 0, int(parts[-3]), int(parts[-2]), int(parts[-1])
        return hour, minute, second, ms

    def parse(self, txt_file_path: str, txt_output_file_path: str) -> None:
        """
        Reads and parses raw file, provided by LLM, in order to set clean structure of it (this includes setting
        proper timecodes for each replica and dealing with overlap zones).
        Writes new transcript to another file with proper timecodes and structure.

        Args:
            txt_file_path (txt): Path to the raw transcript file.
            txt_output_file_path (txt): Path to the new file to save structured transcript.

        Returns:
            None
        """
        txt_file_path = os.path.abspath(txt_file_path)
        # delete file if such exists in order to start with new file
        FileUtils.delete_file(txt_output_file_path)

        with open(txt_file_path, "r") as raw_file:
            lines = [line.strip() for line in raw_file]

        all_chunks = []
        for is_content, group in groupby(lines, key=lambda x: bool(x.strip())):
            if is_content:
                chunk = "\n".join(group)
                all_chunks.append(chunk)

        final_lines = self._remove_excessive_overlap_speech(all_chunks)
        # write (append) to a new file
        with open(txt_output_file_path, 'a') as output_file:
            for line in final_lines:
                output_file.write(f"{line}\n")

        return None

    def _remove_excessive_overlap_speech(self, raw_chunks: list[str]) -> list[str]:
        final_lines = []

        for i, chunk_text in enumerate(raw_chunks):
            lines = chunk_text.strip().split("\n")
            chunk_offset_ms = i * self.step_ms
            cutoff_ms = (i + 1) * self.step_ms if i < len(raw_chunks) - 1 else float("inf")

            for line in lines:
                # searching for timecodes; if there are no timecodes in the line, just go to the next line.
                match = re.search(self.TIMECODE_PATTERN, line)
                if not match:
                    continue

                start_str, end_str = match.groups()

                thirty_sec_in_ms = TimeUtils.convert_to_ms(0, 0, 30, 0)

                real_timecode_start_ms = TimeUtils.convert_to_ms(*self._parse_timecode(start_str))
                real_timecode_end_ms = TimeUtils.convert_to_ms(*self._parse_timecode(end_str))

                real_timecode_start = real_timecode_start_ms + chunk_offset_ms
                real_timecode_end = real_timecode_end_ms + chunk_offset_ms

                if (real_timecode_start >= cutoff_ms + thirty_sec_in_ms) or (real_timecode_start_ms < thirty_sec_in_ms):
                    continue

                start_time_tuple = TimeUtils.convert_ms_to_normal(real_timecode_start)
                end_time_tuple = TimeUtils.convert_ms_to_normal(real_timecode_end)

                start_time_formatted = TimeUtils.format_time_str(*start_time_tuple)
                end_time_formatted = TimeUtils.format_time_str(*end_time_tuple)

                new_timecodes = (f"[{start_time_formatted} --> "
                                 f"{end_time_formatted}]")

                speaker = self._get_speaker(line)
                speaker = self._generate_unique_speaker_id(speaker, i)  # get new speaker id
                speech = self._get_speech(line)

                is_valid_speech = self._validate_speech_text(speech)
                if not is_valid_speech:
                    continue

                final_line_in_ts = f"{speaker} | {new_timecodes} | {speech}"
                final_lines.append(final_line_in_ts)

        return final_lines

    def _get_speaker(self, line: str) -> str:
        """
        Searches for speaker id in the line. It works with LLM output, as it expects symbol ':' right after speaker id.
        Example:
            [01:24:499 - 01:25:799] SPEAKER_01: What is it?   -> SPEAKER_01

        Args:
            line (str): Single line in the transcript.
        Returns:
            str: Speaker id.
        """
        match_speaker = re.search(self.SPEAKER_PATTERN, line)
        if match_speaker:
            speaker_id = match_speaker.group(1)
            return speaker_id
        return ""

    def _get_speech(self, line: str) -> str:
        """
        Searches for speech in the line. It works with LLM output.
        Example:
            [01:24:499 - 01:25:799] SPEAKER_01: What is it?  -> What is it?

        Args:
            line (str): Single line in the transcript.
        Returns:
            str: Speech in the given line from the transcript.

        """
        match_speech = re.search(self.SPEECH_PATTERN, line)
        if match_speech:
            speech = match_speech.group(1)
            return speech
        return ""

    def _generate_unique_speaker_id(self, original_speaker_id: str, chunk_number: int) -> str:
        """
        Generated new speaker id respectively to the number of chunk where it is located.
        It is done in order to distinguish two speakers with the same ids, which are in different chunks (as they
        are different speakers).
        SPEAKER_<num> -> SPEAKER_<chunk_num>_<num>

        For example, new speaker id for SPEAKER_2 in chunk 1 will be: SPEAKER_1_2

        Args:
            original_speaker_id (str): Current speaker id.
            chunk_number (int): The chunk number.
        Returns:
            str: New speaker id.
        """
        match_num = re.search(self.SPEAKER_PERSONAL_NUM_PATTERN, original_speaker_id)
        if match_num:
            old_id = match_num.group(1)
            return f"SPEAKER_{chunk_number}_{old_id}"
        return original_speaker_id

    def _validate_speech_text(self, speech: str) -> bool:
        """
        In some cases, LLM may not add any speech from the speaker. Instead, there may be just comments about the sound.
        For example, [Noise], [Melody] and so on.
        This method just searches for brackets ( '()' and '[]') in the given string.

        If the detected speech text contains that kind of text, then this line should be removed from the transcript.

        Args:
            speech (str): Detected speech in the transcript line.

        Returns:
            bool: True if speech is valid. False if speech must be removed from the transcript due to the absense of
            spoken text.
        """
        speech = speech.strip()
        match_one = re.search(r"\(.*\)", speech)
        match_two = re.search(r"\[.*\]", speech)
        return False if match_one or match_two else True
