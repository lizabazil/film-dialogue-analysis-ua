import re
from src.utils.time_utils import TimeUtils
from src.utils.file_utils import FileUtils
import os
from itertools import groupby


def _get_speaker(line: str) -> str:
    match_speaker = re.search(r"(SPEAKER.*?):", line)
    if match_speaker:
        speaker_id = match_speaker.group(1)
        return speaker_id
    return ""


def _get_speech(line: str) -> str:
    match_speech = re.search(r"SPEAKER_\w+:\s+(.*)", line)
    if match_speech:
        speech = match_speech.group(1)
        return speech
    return ""


def _format_time_str(h, m, s, ms) -> str:
    """
    Formats into proper string. For example, with given input h=1, m=21, s=34, ms=334, the result will be string:
    '01:21:34.334'.
    """
    return f"{h:02}:{m:02}:{s:02}.{ms:03}"


class LLMTranscriptMerger:
    """
    This class is used for reading and parsing output (full transcription for a single audio/movie) from the LLM.
    It creates new text file with cleaned transcript and proper timecodes.
    """
    TimeCode = tuple[int, int, int, int]  # hour, minute, second, millisecond

    def __init__(self, chunk_length_in_min: int, overlap_in_min: float):
        self.chunk_length_in_min = chunk_length_in_min
        self.overlap_in_min = overlap_in_min
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

    def read_raw_transcript_file_from_llm(self, txt_file_path: str, txt_output_file_path: str):
        """
        Reads and parses raw file, provided by LLM, in order to set clean structure of it.
        Writes new transcript to another file with proper timecodes
        """
        txt_file_path = os.path.abspath(txt_file_path)
        #speaker_id, speech, chunk_id = None, None, 0
        FileUtils.delete_file(txt_output_file_path)

        with open(txt_file_path, "r") as raw_file:
            lines = [line.strip() for line in raw_file]

        all_chunks = []
        for is_content, group in groupby(lines, key=lambda x: bool(x.strip())):
            if is_content:
                chunk = "\n".join(group)
                all_chunks.append(chunk)

        # for line in lines:
        #     print(f"\nLINE:\n{line}")
        #
        #     # get the chunk number if it is line with this information
        #     if line.startswith("-- CHUNK "):
        #         chunk_id = int(re.findall(r"\d+", line)[0])
        #         continue
        #
        #     timecodes = re.findall(r"\[(.*?)]", line)[0]  # get everything between '[' and ']'
        #     timecode_start, timecode_end = timecodes.split(" - ")
        #     timecode_start = self._parse_timecode(timecode_start)
        #     timecode_end = self._parse_timecode(timecode_end)
        #
        #     # set to proper timecode (according to the whole movie)
        #     timecode_start_h, timecode_start_m, timecode_start_s, timecode_start_ms = self._set_to_proper_timecode(
        #         chunk_id,
        #         timecode_start)
        #
        #     timecode_end_h, timecode_end_m, timecode_end_s, timecode_end_ms = self._set_to_proper_timecode(chunk_id,
        #                                                                                                    timecode_end)
        #
        #     speaker_id = _get_speaker(line)
        #     speech = _get_speech(line)
        #
        #     output_line = (
        #         f"{speaker_id} | {timecode_start_h}:{timecode_start_m}:{timecode_start_s}.{timecode_start_ms}"
        #         f" --> {timecode_end_h}:{timecode_end_m}:{timecode_end_s}.{timecode_end_ms} | "
        #         f"{speech}")

        final_lines = self._remove_expressive_overlap_speech(all_chunks)
        # write (append) to a new file
        with open(txt_output_file_path, 'a') as output_file:
            for line in final_lines:
                output_file.write(f"{line}\n")

    def _remove_expressive_overlap_speech(self, raw_chunks: list[str]) -> list[str]:
        final_lines = []
        for i, chunk_text in enumerate(raw_chunks):
            lines = chunk_text.strip().split("\n")
            chunk_offset_ms = i * self.step_ms
            cutoff_ms = (i + 1) * self.step_ms if i < len(raw_chunks) - 1 else float("inf")

            for line in lines:
                # searching for timecodes
                match = re.search(r"\[(.*?)\s*-\s*(.*?)]", line)
                if not match:
                    continue

                start_str, end_str = match.groups()

                real_timecode_start_ms = TimeUtils.convert_to_ms(*self._parse_timecode(start_str))
                real_timecode_end_ms = TimeUtils.convert_to_ms(*self._parse_timecode(end_str))

                real_timecode_start = real_timecode_start_ms + chunk_offset_ms
                real_timecode_end = real_timecode_end_ms + chunk_offset_ms

                if real_timecode_start >= cutoff_ms:
                    continue

                start_time_tuple = TimeUtils.convert_ms_to_normal(real_timecode_start)
                end_time_tuple = TimeUtils.convert_ms_to_normal(real_timecode_end)

                start_time_formatted = _format_time_str(*start_time_tuple)
                end_time_formatted = _format_time_str(*end_time_tuple)

                new_timecodes = (f"[{start_time_formatted} --> "
                                 f"{end_time_formatted}]")

                speaker = _get_speaker(line)
                speech = _get_speech(line)

                final_line_in_ts = f"{speaker} | {new_timecodes} | {speech}"
                final_lines.append(final_line_in_ts)

        return final_lines
