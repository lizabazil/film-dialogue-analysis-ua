from src.utils.segment import Segment
import re


class SrtTranscriptParser:
    REPLICA_NUMBER_PATTERN = re.compile(r"\d+")
    SRT_TIMECODE_PATTERN = re.compile(r"\d+:\d+:\d+,\d+\s*-->\s*\d+:\d+:\d+,\d+")
    SPEAKER_PATTERN = re.compile(r"[А-ЩЬЮЯҐЄІЇа-щьюяґєіїa-zA-Z0-9\w]+")

    TimeCode = tuple[int, int, int, int]  # h, m, s, ms

    def __init__(self):
        pass

    def parse(self, srt_file_path: str) -> list[Segment]:
        with open(srt_file_path, "r", encoding="utf-8") as srt_file:
            lines = [l for line in srt_file if (l := line.strip())]

        current_segment = None
        parsed_segments = []

        for line in lines:
            if self._is_replica_number(line):  # exsessive info (id of replica), go to the next line
                if current_segment is not None:
                    parsed_segments.append(current_segment)

                current_segment = Segment()
                continue

            if self._is_timecode_string(line):  # have found the line with timecodes
                start_timecode, end_timecode = self._split_timecode_line_into_direct_timecode_strings(line)
                parsed_start_timecode_tuple = self._parse_timecode(start_timecode)  # tuple
                parsed_end_timecode_tuple = self._parse_timecode(end_timecode)  # tuple

                current_segment.set_start_time(*parsed_start_timecode_tuple)
                current_segment.set_end_time(*parsed_end_timecode_tuple)

            else:  # speech text
                speaker = self._infer_speaker_from_replica(line)
                if speaker:
                    current_segment.speaker_id = speaker

                speech = self._get_speech(line)
                if speech:
                    if current_segment.speech:
                        current_segment.speech += (" " + speech)
                    else:
                        current_segment.speech = speech

        if current_segment is not None:
            parsed_segments.append(current_segment)

        return parsed_segments

    def _get_speech(self, line: str) -> str:
        line_without_speaker = self.SPEAKER_PATTERN.sub("", line)
        clean_text = line_without_speaker.lstrip(" :.-")  # clean exsessive symbols from the left
        return clean_text

    def _parse_timecode(self, timecode: str) -> TimeCode:
        # remove all non-decimal and not :., symbols
        timecode = re.sub("[^0-9:,.]", "", timecode)
        parts = re.split(r"[:.,]", timecode)
        try:
            hour = int(parts[0])
            minute = int(parts[1])
            second = int(parts[2])
            ms = int(parts[3])
        except ValueError:
            return 0, 0, 0, 0
        return hour, minute, second, ms

    def _split_timecode_line_into_direct_timecode_strings(self, timecode_line: str) -> tuple[str, str]:
        """
        Splits a raw subtitle timeline string into start and end timecode strings.

        Expects a standard SRT format line, e.g., '00:00:01,000 --> 00:00:04,000'.
        The method ensures the separator '-->' is present exactly once and removes surrounding whitespace from the
        resulting timestamps.

        Args:
            timecode_line (str): The line containing the time range from the subtitle file.

        Returns:
            tuple[str, str]: A tuple containing (start_time_str, end_time_str).

        Raises:
            ValueError: If the line does not contain exactly one '-->' separator, indicating a malformed timecode line.
            """
        parts = timecode_line.split("-->")
        if len(parts) != 2:
            raise ValueError(f"Not able to split the timecode line: {timecode_line}")
        return parts[0].strip(), parts[1].strip()

    def _is_replica_number(self, line: str) -> bool:
        match = self.REPLICA_NUMBER_PATTERN.fullmatch(line.strip())  # match the full line
        return True if match is not None else False

    def _is_timecode_string(self, line: str) -> bool:
        match = self.SRT_TIMECODE_PATTERN.fullmatch(line.strip())
        return True if match is not None else False

    def _infer_speaker_from_replica(self, line: str) -> str:
        """

        Args:
            line:

        Returns:

        """
        match = self.SPEAKER_PATTERN.search(line.strip())
        if match is not None:
            speaker_with_brackets = match.group()
            speaker = re.sub(r"[\[\]]", "", speaker_with_brackets)
            return speaker
        return ""
