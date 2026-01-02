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
