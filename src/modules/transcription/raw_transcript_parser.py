from src.utils.segment import Segment
from src.utils.time_utils import TimeUtils


class RawTranscriptParser:
    """
    Parses a raw text file (transcript) with timestamps, speaker IDs and replicas into structured segments.
    The file much contain data, where each line is in format like this:
    SPEAKER_<number> | <hh:mm:ss.mmm> --> <hh:mm:ss.mmm> | <text>
    """

    def parse(self, txt_file_path: str) -> list[Segment]:
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
            timecode_end = timecode.split('-->')[1].strip()
            speech = line.split('|')[2].strip()

            # get start hour, minute, second and ms
            start_h, start_m, start_s, start_ms = TimeUtils.get_h_m_s_ms_from_the_string(timecode_start)
            end_h, end_m, end_s, end_ms = TimeUtils.get_h_m_s_ms_from_the_string(timecode_end)
            segment = Segment(speaker, start_h=start_h, start_m=start_m, start_s=start_s, start_ms=start_ms,
                              end_h=end_h, end_m=end_m, end_s=end_s, end_ms=end_ms, speech=speech)
            segments.append(segment)

        return segments
