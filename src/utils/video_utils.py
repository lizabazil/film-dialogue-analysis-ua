import cv2
import numpy as np
from src.utils.time_utils import TimeUtils
import subprocess


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

    @staticmethod
    def get_duration_of_video(video_path: str) -> tuple:
        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                 "format=duration", "-of",
                                 "default=noprint_wrappers=1:nokey=1",
                                 "-sexagesimal",
                                 video_path],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        decoded_duration = result.stdout.decode("utf-8").strip()
        print("type", type(decoded_duration))
        print("RESULT", decoded_duration)

        parsed_to_normal = VideoUtils._parse_duration_output(decoded_duration)
        return parsed_to_normal

    @staticmethod
    def _parse_duration_output(output_duration: str) -> tuple:
        split = output_duration.split(":")
        hour, minute = split[0], split[1]
        seconds = split[2].split(".")[0]
        return hour, minute, seconds
