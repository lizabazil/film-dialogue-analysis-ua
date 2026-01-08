# TODO: implement
from basic_gender_extractor import BasicGenderExtractor
from src.utils.segment import Segment


class TextGenderExtractor(BasicGenderExtractor):
    def __init__(self):
        super().__init__()

    def predict_gender(self, video_path: str, segment: Segment) -> dict | None:
        pass
