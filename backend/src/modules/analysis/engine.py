from src.modules.analysis.schemas import MovieAnalysisReport
from src.utils.segment import Segment
from src.modules.analysis.metrics.gender_stats import GenderStatsMetric
from src.modules.analysis.metrics.metadata import MetaDataMetric


class AnalysisEngine:
    def __init__(self):
        self.metrics = {
            "gender": GenderStatsMetric(),
            "metadata": MetaDataMetric()
        }

    def run_full_analysis(self, segments: list[Segment], video_path: str) -> MovieAnalysisReport:
        """

        Args:
            segments: Segments, where fields 'nlp_data' and 'gender' are already filled.
            video_path: Path to the given video.

        Returns:

        """
        gender_metrics_data = self.metrics["gender"].calculate(segments)
        metadata = self.metrics["metadata"].calculate(segments, video_path=video_path)
        return MovieAnalysisReport(
            gender_stats=gender_metrics_data,
            metadata=metadata
        )
