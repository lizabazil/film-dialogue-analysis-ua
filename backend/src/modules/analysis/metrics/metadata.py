from src.utils.segment import Segment
from src.modules.analysis.metrics.base import BaseMetric
from src.utils.video_utils import VideoUtils
import os


class MetaData(BaseMetric):
    def calculate(self, segments: list[Segment], **kwargs) -> dict:
        video_path = kwargs.get("video_path")
        filename = os.path.basename(video_path)
        hour, minute, seconds = VideoUtils.get_duration_of_video(video_path)

        duration_in_minutes = hour * 60 + minute
        duration_in_seconds = hour * 3600 + minute * 60 + seconds
        formatted_duration = f"{hour:02}:{minute:02}:{seconds:02}"
        file_size_in_gb = self._get_file_size_gb(video_path)

        return {
            "filename": filename,
            "duration_minutes": duration_in_minutes,
            "duration_seconds": duration_in_seconds,
            "formatted_duration": formatted_duration,
            "file_size_gb": file_size_in_gb
        }

    def _get_file_size_gb(self, video_path: str) -> float:
        file_size_bytes = os.path.getsize(video_path)
        file_size_gb = file_size_bytes / (1024 ** 3)
        return file_size_gb
