import subprocess
from pydub import AudioSegment


class AudioFileUtils:
    @staticmethod
    def extract_audio_from_video(video_path: str, audio_path: str) -> None:
        """
        Converts the video file to an audio file using ffmpeg.

        Args:
            video_path (str): Path to the input video file.
            audio_path (str): Path to the output audio file.

        Returns:
            None
        """
        command = [
            "ffmpeg",
            "-i", video_path,
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ar', '16000',  # to 16 kHz
            '-ac', '1',  # to one audio channel
            '-y',  # overwrite output file if exists
            audio_path
        ]
        try:
            subprocess.run(command, check=True)
        except Exception as e:
            print(f"Error during audio extraction: {e}")
        return None

    @staticmethod
    def cut_audio_segment(input_file_path: str, output_file_path: str,
                           start_h: float, start_min: float, start_sec: float, start_ms: float,
                           end_h: float, end_min: float, end_sec: float, end_ms: float) -> None:
        """
        Cuts a segment from an audio file and saves it as a new file.
        Args:
            input_file_path (str): Path to the input audio file.
            output_file_path (str): Path to save the output audio segment.
            start_h (float): Start time hours.
            start_min (float): Start time minutes.
            start_sec (float): Start time seconds.
            start_ms (float): Start time milliseconds.
            end_h (float): End time hours.
            end_min (float): End time minutes.
            end_sec (float): End time seconds.
            end_ms (float): End time milliseconds.

        Returns:
            None
        """
        audio = AudioSegment.from_file(input_file_path, format="mp3")

        start = ((start_h * 3600 + start_min * 60) + start_sec) * 1000 + start_ms
        end = ((end_h * 3600 + end_min * 60) + end_sec) * 1000 + end_ms

        mid_seconds = audio[start:end]
        mid_seconds.export(output_file_path, format="mp3")
        #print("New Audio file is created and saved")
        return None
