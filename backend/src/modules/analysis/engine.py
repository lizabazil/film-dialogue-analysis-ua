from src.modules.analysis.schemas import MovieAnalysisReport
from src.utils.segment import Segment
from src.modules.analysis.metrics.gender_stats import GenderStatsMetric
from src.modules.analysis.metrics.metadata import MetaDataMetric
from src.modules.analysis.metrics.speaker_lexicon import SpeakerLexicon


class AnalysisEngine:
    def __init__(self):
        self.metrics = {
            "gender": GenderStatsMetric(),
            "metadata": MetaDataMetric(),
            "speaker_lexicon": SpeakerLexicon()
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
        speaker_lexicon = self.metrics["speaker_lexicon"].calculate(segments)
        return MovieAnalysisReport(
            gender_stats=gender_metrics_data,
            metadata=metadata,
            speaker_lexicon=speaker_lexicon
        )
