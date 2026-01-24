from src.modules.speaker_enrichment.visual_gender_extractor import VisualGenderExtractor
from src.modules.speaker_enrichment.audio_gender_extractor import AudioGenderExtractor
import yaml
from src.utils.segment import Segment


def visual_extractor(video_path: str, segment: Segment):
    with open("/home/liza/PycharmProjects/film-dialogue-analysis-ua/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    extractor = VisualGenderExtractor(config)
    print("init done")
    #extractor.use_clip_classification_model("/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/screenshots/screen04.jpg")

    res = extractor.predict_gender(video_path, segment)
    print(res)


def audio_extractor(video_path: str, segment: Segment, config: dict):
    extractor = AudioGenderExtractor(config)
    res = extractor.predict_gender(video_path, segment)
    print(f"Audio gender extractor result: {res}")


if __name__ == "__main__":
    segment = Segment("", 0, 1, 24, 499, 0, 1, 25, 799, "")
    video_path = "/home/liza/Documents/Study/diploma/storozhowa_zastawa.mkv"

    with open("/home/liza/PycharmProjects/film-dialogue-analysis-ua/config.yaml", "r") as f:
        config = yaml.safe_load(f)

    audio_extractor(video_path, segment, config)