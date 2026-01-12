# will be using image-to-text model to identify person on the image
from basic_gender_extractor import BasicGenderExtractor
import torch
from transformers import (AutoModel, AutoProcessor, AutoModelForZeroShotObjectDetection)
from PIL import Image
import cv2
import numpy as np
from src.utils.time_utils import TimeUtils
from src.utils.video_utils import VideoUtils
from src.utils.segment import Segment
from src.utils.image_utils import ImageUtils
from src.utils.gender_extractor_return_type import GenderExtractorReturnType


class VisualGenderExtractor(BasicGenderExtractor):
    # paths mostly for debugging
    save_screenshot_path = "../../../data/screenshots/screen_temp.jpg"
    save_cropped_image_path = "../../../data/screenshots/screen_crop.jpg"
    save_screenshot_with_points = "../../../data/screenshots/screen_with_points.jpg"

    def __init__(self, config: dict):
        super().__init__()
        self.model_name = config.get("speaker_enrichment", {}).get("image_model_name", "")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = AutoProcessor.from_pretrained(self.model_name)
        self.model = AutoModelForZeroShotObjectDetection.from_pretrained(self.model_name).to(self.device)

        self.siglip_model = AutoModel.from_pretrained(config.get("speaker_enrichment", {}).
                                                              get("siglip_model_name", ""))
        self.siglip_processor = AutoProcessor.from_pretrained(config.get("speaker_enrichment", {})
                                                              .get("siglip_processor", ""))

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

        image_bgr = VideoUtils.take_screenshot(video_path, middle_h, middle_m, middle_s,
                                               middle_ms,
                                               save_path=self.save_screenshot_path)  # BGR format from OpenCV
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        # grounding dino model inference for getting found boxes
        boxes, scores, text_labels = self._use_grounding_dino_model(image_rgb)

        if len(boxes) > 0:
            all_detected_objects = zip(boxes, scores, text_labels)

            best_box_tensor, best_score, best_label = max(all_detected_objects,
                                                          key=lambda x: self._get_area_of_bounding_box(x[0].tolist()))

            best_box_list = best_box_tensor.tolist()
            ImageUtils.crop_image_with_given_coordinates(self.save_screenshot_path, self.save_cropped_image_path,
                                                         best_box_list[0], best_box_list[1], best_box_list[2],
                                                         best_box_list[3])
            # send the biggest box to the classification model
            #label, score = self.use_clip_classification_model(self.save_cropped_image_path)
            label, score = self._use_siglip_model(self.save_cropped_image_path)
            return {"label": label, "score": score}
        return None

    def _use_grounding_dino_model(self, image: np.ndarray, text_request: str = "a person.") -> (
            tuple)[torch.Tensor, torch.Tensor, list]:
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
        pil_image = Image.fromarray(image)
        for box, score, labels in zip(result["boxes"], result["scores"], result["text_labels"]):
            box = box.tolist()
            print(f"Detected {labels} with confidence {round(score.item(), 3)} at location {box}")
            # draw bounding box for debugging
            #ImageUtils.draw_bounding_box_on_the_image(box, Image.fromarray(image))
            ImageUtils.draw_bounding_box_on_the_image_in_place(box, pil_image)
        # save final image with all the boxes
        pil_image.save(self.save_screenshot_with_points)  # for debugging

        return result["boxes"], result["scores"], result["text_labels"]

    def _use_siglip_model(self, image_path: str) -> tuple[str, float]:
        """
        To use Siglip in order to determine whether there is a woman or a mam on the image.

        Args:
            image_path (str): Path to the given image.

        Returns:
            tuple[str, float]: To use Siglip model to determine whether there is a woman or a man in the image.
            A tuple, where the string is either 'woman' or 'man', with the probability (float) of this
            gender being in the image. The returned name of gender has a higher probability of being in the image
            than the other.
        """
        image = Image.open(image_path)
        texts = ["A photo of a woman", "A photo of a man"]
        inputs = self.siglip_processor(text=texts, images=image, padding="max_length", return_tensors="pt")

        with torch.no_grad():
            outputs = self.siglip_model(**inputs)

        logits_per_image = outputs.logits_per_image
        probs = torch.sigmoid(logits_per_image)  # these are the probabilities

        print(f"{probs[0][0]}% that image 0 is '{texts[0]}'")
        print(f"{probs[0][1]}% that image 0 is '{texts[1]}'")

        woman_prob = probs[0][0].item()
        man_prob = probs[0][1].item()

        if woman_prob >= man_prob:
            return "woman", woman_prob
        else:
            return "man", man_prob

    @staticmethod
    def _get_area_of_bounding_box(bbox: list) -> float:
        """
        Calculates the area of a bounding box.
        """
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        return width * height
