# will be using image-to-text model to identify person on the image
from src.modules.speaker_enrichment.basic_gender_extractor import BasicGenderExtractor
import torch
from transformers import (AutoProcessor, AutoModelForZeroShotObjectDetection)
from PIL import Image
import cv2
import numpy as np
from src.utils.time_utils import TimeUtils
from src.utils.video_utils import VideoUtils
from src.utils.segment import Segment
from src.utils.gender_extractor_return_type import GenderExtractorReturnType
from pathlib import Path
import secrets
import string
import os


class VisualGenderExtractor(BasicGenderExtractor):

    def __init__(self, config: dict):
        super().__init__()
        self.model_name = config.get("speaker_enrichment", {}).get("image_model_name", "")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = AutoProcessor.from_pretrained(self.model_name)
        self.model = AutoModelForZeroShotObjectDetection.from_pretrained(self.model_name).to(self.device)

    def _create_temp_screenshot_path(self, h, m, s, ms) -> str:
        # add segment time to the file name, for example, 01_22_30_500
        time_mark = f"{h:02d}_{m:02d}_{s:02d}_{ms:03d}"
        random_suffix = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(6))

        directory = Path("../../../data/screenshots")
        directory.mkdir(parents=True, exist_ok=True)

        return str(directory / f"screenshot_{time_mark}_{random_suffix}.jpg")

    def predict_gender(self, video_path: str, segment: Segment) -> GenderExtractorReturnType | None:
        """
        Predicts the speaker's gender using visual data from video segments and an image-to-text model.
        Returns:
            dict | None: The dictionary is in format {"label": ..., "score": ...}. Returns None in case if no people
            were found on the image at all.
        """
        middle_h, middle_m, middle_s, middle_ms = TimeUtils.get_middle_point(
            segment.start_h, segment.start_m, segment.start_s, segment.start_ms,
            segment.end_h, segment.end_m, segment.end_s, segment.end_ms
        )

        current_screenshot_path = self._create_temp_screenshot_path(middle_h, middle_m, middle_s, middle_ms)
        try:
            image_bgr = VideoUtils.take_screenshot(video_path, middle_h, middle_m, middle_s,
                                                   middle_ms,
                                                   save_path=current_screenshot_path)  # BGR format from OpenCV

            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            # grounding dino model inference for getting found boxes
            boxes, scores, text_labels = self._use_grounding_dino_model(image_rgb, text_request="man . woman .")

            if len(boxes) > 0:
                all_detected_objects = zip(boxes, scores, text_labels)

                # filter only to leave valid objects (those objects which have only one result class, as the model may
                # give result as "man woman"
                valid_objects = [
                    obj for obj in all_detected_objects
                    if not ("man" in obj[2] and "woman" in obj[2])
                ]

                if not valid_objects:
                    return None

                best_box_tensor, best_score, best_label = max(valid_objects,
                                                              key=lambda x: self._get_area_of_bounding_box(x[0].tolist()))

                return {"label": best_label, "score": best_score.item()}
            return None
        finally:
            if os.path.exists(current_screenshot_path):
                os.remove(current_screenshot_path)

    def _use_grounding_dino_model(self, image: np.ndarray, text_request: str = "a person.") -> (
            tuple)[torch.Tensor, torch.Tensor, list]:
        """
        Uses Grounding DINO model to detect objects in the given image.
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
        pil_image = Image.fromarray(image)
        for box, score, labels in zip(result["boxes"], result["scores"], result["text_labels"]):
            box = box.tolist()
            # draw bounding box for debugging
            #ImageUtils.draw_bounding_box_on_the_image(box, Image.fromarray(image))
            #ImageUtils.draw_bounding_box_on_the_image_in_place(box, pil_image)
        # save final image with all the boxes
        #pil_image.save(self.save_screenshot_with_points)  # for debugging

        return result["boxes"], result["scores"], result["text_labels"]

    @staticmethod
    def _get_area_of_bounding_box(bbox: list) -> float:
        """
        Calculates the area of a bounding box.
        """
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width * height
