from abc import ABC, abstractmethod
from src.utils.segment import Segment
from src.utils.gender_extractor_return_type import GenderExtractorReturnType


class BasicGenderExtractor(ABC):
    """
    Basic class with abstract method to set a way of predicting speaker's gender by numerous segments.
    """
    @abstractmethod
    def predict_gender(self, video_path: str, segment: Segment) -> GenderExtractorReturnType | None:
        """
        Predicts the gender of the speaker. Returns result in a dictionary format (label, score) or None if it is not
        possible to detect gender.

        Args:
            video_path (str): The path to the given video.
            segment (Segment): One segment, which represents one replica with additional data.
        """
        pass
