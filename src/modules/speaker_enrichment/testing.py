from src.modules.speaker_enrichment.visual_gender_extractor import VisualGenderExtractor
import yaml
from src.utils.segment import Segment


with open("/home/liza/PycharmProjects/film-dialogue-analysis-ua/config.yaml", "r") as f:
    config = yaml.safe_load(f)

video_path = "/home/liza/Documents/Study/diploma/storozhowa_zastawa.mkv"
extractor = VisualGenderExtractor(config, video_path)
print("init done")
#extractor.use_clip_classification_model("/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/screenshots/screen04.jpg")

segment = Segment("", 0, 23, 50, 0, 0, 23, 50, 600, "")
extractor.predict_gender(segment)