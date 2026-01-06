# will be using image-to-text model to identify person on the image
from basic_gender_extractor import BasicGenderExtractor
import torch
from transformers import (AutoProcessor, AutoModelForZeroShotObjectDetection, CLIPProcessor, CLIPModel)
from PIL import Image, ImageDraw
import cv2
import numpy as np
from src.utils.time_utils import TimeUtils
from src.utils.video_utils import VideoUtils
from src.utils.segment import Segment


def draw_bounding_box(bbox: list, image: Image.Image,
                      output_image_path: str = '/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/screenshots/screen_with_points.jpg') -> None:
    """
    For debugging and testing purposes.
    """
    draw = ImageDraw.Draw(image)
    x1, y1, x2, y2 = int(bbox[0]), int(bbox[1]), int(bbox[2]), int(bbox[3])
    draw.rectangle([x1, y1, x2, y2], outline="white", width=2)
    image.save(output_image_path)
    return None


def crop_image_with_given_coordinates(original_image_path: str, save_cropped_image_path: str,
                                      left: float, upper: float, right: float, lower: float) -> None:
    """
    Crops image with the given path and saves with given output for new image.
    """
    box = (left, upper, right, lower)
    original_image = Image.open(original_image_path)
    cropped_image = original_image.crop(box)
    cropped_image.save(save_cropped_image_path)
    return None


class VisualGenderExtractor(BasicGenderExtractor):
    def __init__(self, config: dict, video_path: str):
        super().__init__()
        self.video_path = video_path
        self.model_name = config.get("speaker_enrichment", {}).get("image_model_name", "")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = AutoProcessor.from_pretrained(self.model_name)
        self.model = AutoModelForZeroShotObjectDetection.from_pretrained(self.model_name).to(self.device)

        self.classification_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14")
        self.classification_processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")

        self.save_screenshot_path = "/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/screenshots/screen_temp.jpg"
        self.save_cropped_image_path = "/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/screenshots/screen_crop.jpg"

    def predict_gender(self, segment: Segment) -> dict | None:
        """
        Predicts the speaker's gender using visual data from video segments and an image-to-text model.
        Returns:
            dict | None: The dictionary is in format {"label": ..., "score": ...}
        """
        middle_h, middle_m, middle_s, middle_ms = TimeUtils.get_middle_point(
            segment.start_h, segment.start_m, segment.start_s, segment.start_ms,
            segment.end_h, segment.end_m, segment.end_s, segment.end_ms
        )

        image_bgr = VideoUtils.take_screenshot(self.video_path, middle_h, middle_m, middle_s,
                                               middle_ms,
                                               save_path=self.save_screenshot_path)  # BGR format from OpenCV
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        # model inference
        self._use_grounding_dino_model(image_rgb)
        return None

    def _use_grounding_dino_model(self, image: np.ndarray, text_request: str = "a man. a woman.") -> None:
        """
        Uses Grounding DINO model to detect objects in the given image.
        https://huggingface.co/IDEA-Research/grounding-dino-base
        """
        # get predictions from the image-to-text model
        text = text_request
        inputs = self.processor(images=image, text=text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)

        height, width, _ = image.shape
        results = self.processor.post_process_grounded_object_detection(
            outputs,
            inputs.input_ids,
            threshold=0.3,
            text_threshold=0.3,
            #target_sizes=[image.size[::-1]]
            target_sizes=[(height, width)]
        )

        result = results[0]
        print("Grounding DINO model results:")
        for box, score, labels in zip(result["boxes"], result["scores"], result["text_labels"]):
            box = box.tolist()
            print(f"Detected {labels} with confidence {round(score.item(), 3)} at location {box}")
            # draw bounding box for debugging
            draw_bounding_box(box, Image.fromarray(image))

        if len(result["boxes"]) > 0:
            all_detected_objects = zip(result["boxes"], result["scores"], result["text_labels"])

            best_box_tensor, best_score, best_label = max(all_detected_objects,
                                                          key=lambda x: self._get_area_of_bounding_box(x[0].tolist()))

            best_box_list = best_box_tensor.tolist()
            crop_image_with_given_coordinates(self.save_screenshot_path, self.save_cropped_image_path,
                                              best_box_list[0], best_box_list[1], best_box_list[2], best_box_list[3])
            self.use_clip_classification_model(self.save_cropped_image_path)

        """
        Type of result[scores]: <class 'torch.Tensor'>
        Type of result[boxes]: <class 'torch.Tensor'>
        Type of result[text_labels]: <class 'list'>
        """
        return None

    def use_clip_classification_model(self, image_path: Image) -> None:
        image = Image.open(image_path)
        inputs = self.classification_processor(text=["a photo of a woman", "a photo of a man"], images=image,
                                               return_tensors="pt",
                           padding=True)
        outputs = self.classification_model(**inputs)
        logits_per_image = outputs.logits_per_image  # this is the image-text similarity score
        probs = logits_per_image.softmax(dim=1)  # we can take the softmax to get the label probabilities
        print(f"Clip model results: {probs}")
        return None

    @staticmethod
    def _get_area_of_bounding_box(bbox: list) -> float:
        """
        Calculates the area of a bounding box.
        """
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width * height


# get results from grounding dino
# filter boxes to leave the biggest
# crop the biggest box
# send cropped image to clip (or another zero-shot classification model)