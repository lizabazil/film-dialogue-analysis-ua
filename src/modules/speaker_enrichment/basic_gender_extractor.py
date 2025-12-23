from abc import ABC, abstractmethod
from segment import Segment


class BasicGenderExtractor(ABC):
    """
    Basic class with abstract method to set a way of predicting speaker's gender by numerous segments.
    """
    @abstractmethod
    def predict_gender(self, segments: list[Segment]) -> dict | None:
        """
        Predicts the gender of the speaker. Returns result in a dictionary format (label, score) or None if it is not
        possible to detect gender.

        Args:
            segments: The input segments containing speaker data (timecodes of start and finish, speech).
            Those segments are full collection of specific speaker's segments.
        """
        pass
