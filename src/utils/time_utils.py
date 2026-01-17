import re


class TimeUtils:
    """
    This class provides utility methods for timecode conversions and calculations.
    """

    @staticmethod
    def convert_ms_to_normal(ms: float) -> tuple[int, int, int, int]:
        """
        Converts milliseconds to hours, minutes, seconds and milliseconds.
        """
        h = int(ms // (3600 * 1000))
        ms %= (3600 * 1000)
        m = int(ms // (60 * 1000))
        ms %= (60 * 1000)
        s = int(ms // 1000)
        ms %= 1000
        return h, m, s, int(ms)

    @staticmethod
    def convert_to_ms(h: float, m: float, s: float, ms: float) -> float:
        """
        Converts hours, minutes, seconds and milliseconds to total milliseconds.
        """
        res = (h * 3600 * 1000) + (m * 60 * 1000) + (s * 1000) + ms
        return res

    @staticmethod
    def get_middle_point(start_h: float, start_m: float, start_s: float, start_ms: float,
                         end_h: float, end_m: float, end_s: float, end_ms: float) -> tuple:
        """
        Calculates the middle point between start and end timecodes.
        Returns:
        tuple: A tuple containing (h, m, s, ms) of the middle point.
        """
        start_time_in_ms = TimeUtils.convert_to_ms(start_h, start_m, start_s, start_ms)
        end_time_in_ms = TimeUtils.convert_to_ms(end_h, end_m, end_s, end_ms)
        middle_time_in_ms = (start_time_in_ms + end_time_in_ms) / 2
        (h, m, s, ms) = TimeUtils.convert_ms_to_normal(middle_time_in_ms)
        return h, m, s, ms

    @staticmethod
    def format_time_str(h: int, m: int, s: int, ms: int) -> str:
        """
        Formats into proper string. For example, with given input h=1, m=21, s=34, ms=334, the result will be string:
        '01:21:34.334'.

        Args:
            h (int): Hour.
            m (int): Minute.
            s (int): Second.
            ms (int): Millisecond.

        Returns:
            str: Formatted string.
        """
        return f"{h:02}:{m:02}:{s:02}.{ms:03}"

    @staticmethod
    def get_h_m_s_ms_from_the_string(timecode: str) -> tuple[int, int, int, int] | None:
        """
        Get hour, minute, second and millisecond from the string in format: 01:45:38.702.
        Args:
             timecode (str): String timecode. Must be in format like 01:45:38.702.
        Returns:
            tuple[int, int, int, int] | None: Hour, minute, second and millisecond from the given string. Returns
            None if an error has occured.
        """
        h, m, s, ms = re.split(r"[:.]", timecode)
        try:
            return int(h), int(m), int(s), int(ms)
        except ValueError as e:
            print(f"Error with getting time from the string: {e}")
        return None
