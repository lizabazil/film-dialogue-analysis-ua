# this file will be using all methods for identifying the gender of the speaker
from audio_gender_extractor import AudioGenderExtractor
from visual_gender_extractor import VisualGenderExtractor
from text_gender_extractor import TextGenderExtractor


class GenderEnricher:
    """
    Main class which uses different approaches to detect the gender of the speaker.
    """
    # TODO: implement
    def __init__(self, config: dict, video_path: str):
        self.weights = {
            "audio": config.get("speaker_enrichment", {}).get("voting_weights", {}).get("audio", {}),
            "image": config.get("speaker_enrichment", {}).get("voting_weights", {}).get("image", {}),
            "text": config.get("speaker_enrichment", {}).get("voting_weights", {}).get("text", {})
        }

        self.audio_gender_extractor = AudioGenderExtractor(config, video_path)
        self.visual_gender_extractor = VisualGenderExtractor(config, video_path)
        self.text_gender_extractor = TextGenderExtractor()

    def annotate_segments(self, segments: list):
        # TODO: implement
        pass
