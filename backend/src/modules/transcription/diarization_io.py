from pyannote.core import Annotation
from pyannote.core import Segment as PyannoteSegment
import re
from src.utils.time_utils import TimeUtils


class DiarizationIO:

    DIARIZATION_REPLICA_PATTERN = re.compile(r"\[\s*(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})\]\s*\w+\s*(SPEAKER_\d+)")

    def __init__(self):
        pass

    def save_diarization(self, annotations: Annotation, file_path: str) -> None:
        """
        Writes the diarization annotations to a text file for storage or caching.

        This method iterates through the timeline of the provided Annotation object and writes each segment to the
        file. The typical output format includes start time, end time, and speaker label for each replica.

        Args:
            annotations (Annotation): The pyannote.core.Annotation object containing the temporal segmentation and
            speaker labels.
            file_path (str): The destination path where the file will be saved (usually in .txt format).

        Returns:
            None

        Raises:
            IOError: If the file cannot be opened or written to.
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            for segment, track_id, speaker in annotations.itertracks(yield_label=True):
                start_hours, start_minutes, start_seconds, start_milliseconds = TimeUtils.convert_seconds_to_proper_format(segment.start)
                end_hours, end_minutes, end_seconds, end_milliseconds = TimeUtils.convert_seconds_to_proper_format(segment.end)

                f.write(f"[{start_hours:02d}:{start_minutes:02d}:{start_seconds:02d}.{start_milliseconds:03d} --> "
                        f"{end_hours:02d}:{end_minutes:02d}:{end_seconds:02d}.{end_milliseconds:03d}] "
                        f"{track_id} {speaker}\n")

    def load_diarization(self, file_path: str) -> Annotation:
        """
        Loads diarization segments from a file and reconstructs the Annotation object.

        This method is the inverse of `save_diarization`. It reads the cached text file, parses the timecodes and
        speaker labels, and repopulates a `pyannote.core.Annotation` object. This allows the pipeline to skip the
        heavy diarization inference step if the results were already saved.

        Args:
            file_path (str): Path to the existing text file containing diarization data (expected format per line:
            '[<start_h:start_m:start_s.start_ms> --> <end_h:end_m:end_s.end_ms>] <speaker_id>').

        Returns:
            Annotation: A reconstructed `pyannote.core.Annotation` object ready for further processing.

        Raises:
            FileNotFoundError: If the specified file does not exist.
        """
        # to find: (start_time_str, end_time_str, speaker_label)
        annotation = Annotation()

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if not line:
                    continue

                match = self.DIARIZATION_REPLICA_PATTERN.search(line)
                if match:
                    start_str, end_str, speaker = match.groups()

                    start_seconds = TimeUtils.parse_time_to_seconds(start_str)
                    end_seconds = TimeUtils.parse_time_to_seconds(end_str)

                    segment = PyannoteSegment(start_seconds, end_seconds)
                    annotation[segment] = speaker

        return annotation
