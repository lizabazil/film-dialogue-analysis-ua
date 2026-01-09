# this file will be using all methods for identifying the gender of the speaker
from audio_gender_extractor import AudioGenderExtractor
from visual_gender_extractor import VisualGenderExtractor
from text_gender_extractor import TextGenderExtractor
from src.utils.segment import Segment


class GenderEnricher:
    """
    Main class which uses different approaches to detect the gender of the speaker.
    """
    # TODO: implement
    def __init__(self, config: dict):
        self.weights = {
            "audio": config.get("speaker_enrichment", {}).get("voting_weights", {}).get("audio", {}),
            "image": config.get("speaker_enrichment", {}).get("voting_weights", {}).get("image", {}),
            "text": config.get("speaker_enrichment", {}).get("voting_weights", {}).get("text", {})
        }
        self.audio_gender_extractor = AudioGenderExtractor(config)
        self.visual_gender_extractor = VisualGenderExtractor(config)
        self.text_gender_extractor = TextGenderExtractor()

    def annotate_segment(self, video_path: str, segment: Segment):
        audio_result = self.audio_gender_extractor.predict_gender(video_path, ...)
        visual_result = self.visual_gender_extractor.predict_gender(video_path, ...)
        text_result = self.text_gender_extractor.predict_gender(..., ...)
        # TODO: implement
        pass
