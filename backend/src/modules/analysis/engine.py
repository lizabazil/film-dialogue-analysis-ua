from schemas import MovieAnalysisReport
from src.utils.segment import Segment


class AnalysisEngine:
    def __int__(self):
        pass

    def run_full_analysis(self, segments: list[Segment]) -> MovieAnalysisReport:
        """

        Args:
            segments: Segments, where fields 'nlp_data' and 'gender' are already filled.

        Returns:

        """
        pass
