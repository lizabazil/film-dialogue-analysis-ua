import cv2
import numpy as np
from src.utils.time_utils import TimeUtils
import subprocess
import os


class VideoUtils:
    @staticmethod
    def take_screenshot(video_path: str, target_h: float, target_m: float, target_s: float, target_ms: float,
                        save_path: str = "") \
            -> np.ndarray | None:
        target_time = TimeUtils.convert_to_ms(target_h, target_m, target_s, target_ms)
        cam = cv2.VideoCapture(video_path)

        if not cam.isOpened():  # couldn't open video file
            return None

        cam.set(cv2.CAP_PROP_POS_MSEC, target_time)
        success, image = cam.read()
        cam.release()
        if success:
            if save_path != "":
                save_path = os.path.abspath(save_path)
                cv2.imwrite(save_path, image)
            return image
        return None

    @staticmethod
    def get_duration_of_video(video_path: str) -> tuple[int, int, int]:
        """
        Get the total duration of the video file.
        Args:
            video_path (str): The path of the given video file.
        Returns:
            tuple[int, int, int] : The hours, minutes and seconds, with the duration for the given file.

        """
        result = subprocess.run([
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            print(f"FFprobe error: {result.stderr}")
            return 0, 0, 0

        try:
            total_seconds = float(result.stdout.strip())
            h, m, s, _ = TimeUtils.convert_seconds_to_proper_format(total_seconds)
            return h, m, s
        except ValueError:
            return 0, 0, 0
