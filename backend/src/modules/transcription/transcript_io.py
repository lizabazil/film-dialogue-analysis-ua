import json
import re
import os

from src.utils.segment import Segment
from src.utils.time_utils import TimeUtils


class TranscriptIO:
    """
    Parses a raw text file (transcript) with timestamps, speaker IDs and replicas into structured segments.
    The file much contain data, where each line is in format like this:
    SPEAKER_<number> | <hh:mm:ss.mmm> --> <hh:mm:ss.mmm> | <text>
    """

    def parse(self, file_path: str) -> tuple[list[Segment], bool]:
        """
        Parses file based on its extension. In case with JSONL file, there already will be genders. Otherwise, there
        won't be genders.
        Args:
            file_path: Path to the file with transcript.

        Returns:
            tuple[list[Segment], bool]: True if there is already genders, False otherwise.
        """
        extension = os.path.splitext(file_path)[1]
        if extension == ".jsonl":
            return self._parse_jsonl(file_path), True
        elif extension == '.txt':
            return self._parse_txt(file_path), False
        else:
            raise ValueError(f"Unknown file format with extension: {extension}")

    def _parse_jsonl(self, jsonl_file_path) -> [list[Segment]]:
        segments = []
        with open(jsonl_file_path, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                segments.append(Segment(*data))

        return segments

    def _parse_txt(self, txt_file_path: str) -> list[Segment]:
        """
        """
        segments = []
        with open(txt_file_path, "r", encoding="utf-8") as f:
            lines = f.read()
        lines = lines.split("\n")

        for line in lines:
            parts = line.split("|")
            if len(parts) < 3:
                continue

            # each line in format like this: SPEAKER_<number> | <hh:mm:ss.mmm> --> <hh:mm:ss.mmm> | <text>
            speaker = line.split("|")[0].strip()
            timecode = line.split("|")[1].strip()
            timecode_start = timecode.split('-->')[0].strip()
            timecode_start = self._remove_brackets(timecode_start)

            timecode_end = timecode.split('-->')[1].strip()
            timecode_end = self._remove_brackets(timecode_end)

            speech = line.split('|')[2].strip()

            # get start hour, minute, second and ms
            start_h, start_m, start_s, start_ms = TimeUtils.get_h_m_s_ms_from_the_string(timecode_start)
            end_h, end_m, end_s, end_ms = TimeUtils.get_h_m_s_ms_from_the_string(timecode_end)
            segment = Segment(speaker, start_h=start_h, start_m=start_m, start_s=start_s, start_ms=start_ms,
                              end_h=end_h, end_m=end_m, end_s=end_s, end_ms=end_ms, speech=speech)
            segments.append(segment)

        return segments

    def save(self, segments: list[Segment], output_file_path: str) -> None:
        """
        Persists the list of transcript segments to a text file in a structured format.

        This method writes each segment to a new line using a pipe-delimited format that includes the speaker ID,
        formatted timestamps, and the spoken text.

        The output format is: 'SPEAKER_ID | [HH:MM:SS.ms --> HH:MM:SS.ms]| SPEECH TEXT'

        Args:
            segments (list[Segment]): A list of processed Segment objects containing speaker IDs, broken-down
            timestamps (h, m, s, ms), and text content.
            output_file_path (str): The destination path for the output file. If the file already exists, it will be
            overwritten.

        Returns:
            None

        Raises:
            IOError: If the system fails to open or write to the specified file.
        """
        with open(output_file_path, "w", encoding="utf-8") as f:
            for segment in segments:
                f.write(f"{segment.speaker_id} | "
                        f"[{TimeUtils.format_time_str(segment.start_h, segment.start_m, segment.start_s, segment.start_ms)} "
                        f" --> {TimeUtils.format_time_str(segment.end_h, segment.end_m, segment.end_s, segment.end_ms)}]"
                        f" | {segment.speech}\n")

    @staticmethod
    def _remove_brackets(timecode: str) -> str:
        """
        Removes brackets '[' or ']' from the string.
        Args:
            timecode: Timecode type string.

        Returns:
            str: String without brackets.

        """
        return re.sub(r"[\[\]]", "", timecode)
