import re
from src.utils.time_utils import TimeUtils
from src.utils.file_utils import FileUtils
import os
from itertools import groupby
import json


class LLMTranscriptParser:
    """
    This class is used for reading and parsing output (full transcription for a single audio/movie) from the LLM.
    It creates new text file with cleaned transcript and proper timecodes.
    """
    SPEAKER_PATTERN = re.compile(r"(SPEAKER.*?):")
    SPEAKER_WITH_GENDER_PATTERN = re.compile(r"(SPEAKER_\d+)\s*\((.*?)\)(?=:)")
    #SPEECH_PATTERN = re.compile(r"SPEAKER_\w+:\s+(.*)")
    SPEECH_PATTERN = re.compile(r"SPEAKER_.*?:[ \t]+(?P<speech>.*)")  # works for files with and without gender marks
    TIMECODE_PATTERN = re.compile(r"\[(.*?)\s*-\s*(.*?)]")
    SPEAKER_PERSONAL_NUM_PATTERN = re.compile(r"SPEAKER_(\d+)")
    GENDER_PATTERN = re.compile(r"\(?([FMU])\)?(?=:)")

    TimeCode = tuple[int, int, int, int]  # hour, minute, second, millisecond

    def __init__(self, config: dict, with_gender_mark: bool = False):
        """

        Args:
            config:
            with_gender_mark: If there is already specified gender in the transcript, then this argument should be
            set to True, otherwise False.
        """
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

    def parse(self, txt_file_path: str, output_file_path: str = "", with_gender_notes: bool = False) -> None:
        """
        Reads and parses raw file, provided by LLM, in order to set clean structure of it (this includes setting
        proper timecodes for each replica and dealing with overlap zones).
        Writes new transcript to another file with proper timecodes and structure.

        Args:
            txt_file_path (txt): Path to the raw transcript file.
            output_file_path (txt): Path to the new file to save structured transcript.
            with_gender_notes (bool): States whether file already has notes about speakers' genders. If it equals to
            True, then the 'output_file_path' is supposed to be a .jsonl file, otherwise output file will be .txt.

        Returns:
            None
        """
        # delete file if such exists in order to start with new file
        FileUtils.delete_file(output_file_path)

        with open(txt_file_path, "r") as raw_file:
            lines = [line.strip() for line in raw_file]

        all_chunks = []
        for is_content, group in groupby(lines, key=lambda x: bool(x.strip())):
            if is_content:
                chunk = "\n".join(group)
                all_chunks.append(chunk)

        final_lines = self._remove_excessive_overlap_speech(all_chunks, with_gender=with_gender_notes)

        # write (append) to a new file
        if not with_gender_notes:  # write to .txt file withour gender notes
            with open(output_file_path, 'a') as output_file:
                for line in final_lines:
                    output_file.write(f"{line}\n")

        elif with_gender_notes:  # output file path is supposed to be .jsonl file
            with open(output_file_path, "a", encoding="utf-8") as f:
                for segment_dict in final_lines:
                    f.write(json.dumps(segment_dict, ensure_ascii=False) + "\n")

        return None

    def _remove_excessive_overlap_speech(self, raw_chunks: list[str], with_gender: bool = False) -> list[str]:
        """
        Processes raw transcript chunks to create a continuous, non-overlapping timeline.

        This method performs several key tasks:
        1. Parses raw text from overlapping processing windows.
        2. Converts relative timestamps (from each chunk) into absolute global timecodes.
        3. Filters out segments that fall outside the valid processing window (overlap handling) to ensure the best
        transcript quality.
        4. Resolves temporal conflicts: If a segment ends after the next segment begins, the end time of the
        preceding segment is truncated to match the start time of the current segment.

        Args:
            raw_chunks (list[str]): A list of raw text strings returned by the model, where each item corresponds
            to a processed audio chunk.

        Returns:
            list[str]: A list of fully formatted strings (e.g., "SpeakerID | [Start --> End] | Text") with corrected
            timestamps and unique speaker IDs.
        """
        final_lines = []
        last_segment = None

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

                if with_gender:  # get speaker and gender at the same time
                    speaker, gender = self._get_speaker_with_gender(line)
                else:
                    speaker = self._get_speaker(line)

                speaker = self._generate_unique_speaker_id(speaker, i)  # get new speaker id
                speech = self._get_speech(line)

                is_valid_speech = self._validate_speech_text(speech)
                if not is_valid_speech:
                    continue
                if not speaker:
                    continue

                current_segment = {
                    "start": real_timecode_start,
                    "end": real_timecode_end,
                    "speaker": speaker,
                    "speech": speech
                }
                if with_gender and gender:  # add gender if such file has it
                    current_segment["gender"] = gender

                if last_segment is not None:
                    if last_segment["end"] > current_segment["start"]:
                        last_segment["end"] = current_segment["start"]

                    self._format_and_append_segment(final_lines, last_segment, with_gender)

                last_segment = current_segment

        if last_segment is not None:
            self._format_and_append_segment(final_lines, last_segment, with_gender)

        return final_lines

    def _format_and_append_segment(self, final_lines_list, segment_data, with_gender: bool = False) -> None:
        """
        Formats the segment data into the final string representation and appends it to the list.
        This method is responsible for the conversion of timestamps (from total ms to string format), which allows
        modifying the 'end' time dynamically before finalizing the line (in case of obvious hallucinations).

        The resulting format is: "Speaker_ID | [HH:MM:SS.mmm --> HH:MM:SS.mmm] | Speech text"

        Args:
            final_lines_list (list): The list of strings where the formatted line will be stored.
            segment_data (dict): A dictionary containing the segment details with keys:
                                     - 'start' (int): Start time in milliseconds.
                                     - 'end' (int): End time in milliseconds.
                                     - 'speaker' (str): The speaker ID.
                                     - 'speech' (str): The recognized text.
        Returns:
            None
        """
        start_time_tuple = TimeUtils.convert_ms_to_normal(segment_data.get('start'))
        end_time_tuple = TimeUtils.convert_ms_to_normal(segment_data.get('end'))

        if with_gender:
            final_line_in_ts = {
            "speaker_id": segment_data.get("speaker"),
            "total_ms_start": segment_data.get("start"),
            "total_ms_end": segment_data.get("end"),
            "start_h": start_time_tuple[0],
            "start_m": start_time_tuple[1],
            "start_s": start_time_tuple[2],
            "start_ms": start_time_tuple[3],
            "end_h": end_time_tuple[0],
            "end_m": end_time_tuple[1],
            "end_s": end_time_tuple[2],
            "end_ms": end_time_tuple[3],
            "speech": segment_data.get("speech"),
            "gender": segment_data.get("gender")
            }
            final_lines_list.append(final_line_in_ts)
            return None

        start_time_formatted = TimeUtils.format_time_str(*start_time_tuple)
        end_time_formatted = TimeUtils.format_time_str(*end_time_tuple)

        new_timecodes = (f"[{start_time_formatted} --> "
                         f"{end_time_formatted}]")

        final_line_in_ts = f"{segment_data['speaker']} | {new_timecodes} | {segment_data['speech']}"
        final_lines_list.append(final_line_in_ts)
        return None

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

    def _get_speaker_with_gender(self, line: str) -> tuple[str, str]:
        match = re.search(self.SPEAKER_WITH_GENDER_PATTERN, line)
        if match:
            speaker_id = match.group(1)
            gender = match.group(2)
            gender_str = "woman" if gender == "F" else "man" if gender == "M" else "unknown"
            return speaker_id, gender_str
        return "", ""

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
            speech = match_speech.group("speech")
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
        This method just searches for brackets ( '(text)', '[text]' and '*text*) in the given string.

        If the detected speech text contains that kind of text, then this line should be removed from the transcript.

        Args:
            speech (str): Detected speech in the transcript line.

        Returns:
            bool: True if speech is valid. False if speech must be removed from the transcript due to the absense of
            spoken text.
        """
        speech = speech.strip()
        if not speech:
            return False
        match_one = re.search(r"\(.*\)", speech)
        match_two = re.search(r"\[.*\]", speech)
        match_three = re.search(r"\*.*\*", speech)
        return False if match_one or match_two or match_three else True
