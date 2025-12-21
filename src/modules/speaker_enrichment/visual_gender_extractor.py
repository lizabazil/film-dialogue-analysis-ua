# will be using image-to-text model to identify person on the image
from basic_gender_extractor import BasicGenderExtractor
import torch
from transformers import (AutoProcessor, AutoModelForZeroShotObjectDetection)
from PIL import Image, ImageDraw
import cv2
import numpy as np
from utils.time_utils import TimeUtils
from utils.video_utils import VideoUtils


def draw_bounding_box(bbox: list, image: Image.Image,
                      output_image_path: str = 'data/screenshots/screen_with_points.jpg') -> None:
    """
    For debugging and testing purposes.
    """
    draw = ImageDraw.Draw(image)
    x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    draw.rectangle([x1, y1, x2, y2], outline="white", width=2)
    image.save(output_image_path)
    return None


class VisualGenderExtractor(BasicGenderExtractor):
    def __init__(self, config: dict, video_path: str):
        super().__init__()
        self.video_path = video_path
        self.model_name = config.get("speaker_enrichment", {}).get("image_model_name", "")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = AutoProcessor.from_pretrained(self.model_name)
        self.model = AutoModelForZeroShotObjectDetection.from_pretrained(self.model_name).to(self.device)

    def predict_gender(self, segments: list) -> dict | None:
        """
        Predicts the speaker's gender using visual data from video segments and an image-to-text model.
        Returns:
            dict | None: The dictionary is in format {"label": ..., "score": ...}
        """
        # TODO: choose a couple of segments to analyze (if there are many)
        # TODO: take screenshots from those segments (at the midpoint of each segment)
        for segment in ...:  # in chosen segments
            middle_h, middle_m, middle_s, middle_ms = TimeUtils.get_middle_point(
                segment["start_h"], segment["start_m"], segment["start_s"], segment["start_ms"],
                segment["end_h"], segment["end_m"], segment["end_s"], segment["end_ms"]
            )

            image_bgr = VideoUtils.take_screenshot(self.video_path, middle_h, middle_m, middle_s,
                                              middle_ms)  # BGR format from OpenCV
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            # model inference
            scores, boxes, labels = self._use_grounding_dino_model(image_rgb)
        return None

    def _use_grounding_dino_model(self, image: np.ndarray, text_request: str = "a man. a woman.") -> tuple:
        """
        Uses Grounding DINO model to detect objects in the given image.
        https://huggingface.co/IDEA-Research/grounding-dino-base
        """
        # get predictions from the image-to-text model
        text = text_request
        inputs = self.processor(images=image, text=text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)

        results = self.processor.post_process_grounded_object_detection(
            outputs,
            inputs.input_ids,
            threshold=0.3,
            text_threshold=0.3,
            target_sizes=[image.size[::-1]]
        )

        result = results[0]
        print("Grounding DINO model results:")
        for box, score, labels in zip(result["boxes"], result["scores"], result["text_labels"]):
            box = box.tolist()
            print(f"Detected {labels} with confidence {round(score.item(), 3)} at location {box}")
            # draw bounding box for debugging
            draw_bounding_box(box, Image.fromarray(image))

        """
        Type of result[scores]: <class 'torch.Tensor'>
        Type of result[boxes]: <class 'torch.Tensor'>
        Type of result[text_labels]: <class 'list'>
        """
        return result["scores"], result["boxes"], result["text_labels"]

    @staticmethod
    def _get_area_of_bounding_box(bbox: list) -> float:
        """
        Calculates the area of a bounding box.
        """
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width * height
