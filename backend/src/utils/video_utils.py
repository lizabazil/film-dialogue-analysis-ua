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
        result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                                 "format=duration", "-of",
                                 "default=noprint_wrappers=1:nokey=1",
                                 "-sexagesimal",
                                 video_path],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        decoded_duration = result.stdout.decode("utf-8").strip()

        parsed_to_normal = VideoUtils._parse_duration_output(decoded_duration)
        return parsed_to_normal

    @staticmethod
    def _parse_duration_output(output_duration: str) -> tuple[int, int, int]:
        split = output_duration.split(":")
        hour, minute = split[0], split[1]
        seconds = split[2].split(".")[0]
        return int(hour), int(minute), int(seconds)

    @staticmethod
    def get_subtitle_track_from_video(video_file_path: str, output_subtitle_path: str, subtitle_track_num: int = 0) -> None:
        if not os.path.exists(video_file_path):
            print(f"Error: video file does not exist: {video_file_path}")
            return None
        command = [
            "ffmpeg",
            "-y",
            "-i", video_file_path,
            "-map", f"0:s:{subtitle_track_num}",
            output_subtitle_path
        ]
        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(output_subtitle_path) and os.path.getsize(output_subtitle_path) > 0:
                print(f"Created subtitle file {output_subtitle_path}")
                return None
            return None

        except subprocess.CalledProcessError:
            print(f"Warning: No subtitle track found or ffmpeg error for {video_file_path}")
            return None
        except Exception as e:
            print(f"Error extracting subtitles: {e}")
            return None

    @staticmethod
    def cut_video_segment(
            input_path: str,
            output_path: str,
            start_h: int, start_m: int, start_s: int, start_ms: int,
            end_h: int, end_m: int, end_s: int, end_ms: int
    ):
        """
        Cuts a video segment based on precise start and end times.
        """
        start_time = f"{start_h:02d}:{start_m:02d}:{start_s:02d}.{start_ms:03d}"
        end_time = f"{end_h:02d}:{end_m:02d}:{end_s:02d}.{end_ms:03d}"

        command = [
            "ffmpeg",
            "-y",
            "-i", input_path,
            "-ss", start_time,
            "-to", end_time,
            "-c:v", "libx264", "-c:a", "aac",
            output_path
        ]

        try:
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"Video segment saved to: {output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error cutting video: {e}")
