import cv2
import numpy as np
from time_utils import TimeUtils


class VideoUtils:
    @staticmethod
    def take_screenshot(video_path: str, target_h: float, target_m: float, target_s: float, target_ms: float) \
            -> np.ndarray | None:
        target_time = TimeUtils.convert_to_ms(target_h, target_m, target_s, target_ms)
        cam = cv2.VideoCapture(video_path)

        if not cam.isOpened():  # couldn't open video file
            return None

        cam.set(cv2.CAP_PROP_POS_MSEC, target_time)
        success, image = cam.read()
        cam.release()
        if success:
            return image
            #cv2.imwrite("data/screenshots/screen.jpg", image)
        return None
