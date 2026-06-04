import os.path
import subprocess
from pydub import AudioSegment
import numpy as np
import torchaudio
import torchaudio.transforms as T


class AudioFileUtils:
    """
    This class provides utility methods for audio file manipulation, including extracting audio from video files,
    and cutting segments from audio files.
    """
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
        video_path = os.path.abspath(video_path)
        audio_path = os.path.abspath(audio_path)

        os.makedirs(os.path.dirname(audio_path), exist_ok=True)

        command = [
            "ffmpeg",
            "-i", video_path,
            '-vn',
            '-acodec', 'libmp3lame',
            '-ar', '16000',
            '-b:a', '64k',
            '-ac', '1',
            '-y',
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
        return None

    @staticmethod
    def cut_audio_segment_in_ms(input_file_path: str, output_file_path: str,
                           start_ms : float, end_ms : float) -> None:
        """
        Cuts a segment from an audio file and saves it as a new file.
        This function differs from the function about that fact, that accepts start and end time in milliseconds
        instead of hours, minute and seconds.
        Args:
            input_file_path (str): Path to the input audio file.
            output_file_path (str): Path to save the output audio segment.
            start_ms (float): Start time expressed in milliseconds.
            end_ms (float): End time expresses in milliseconds.

        Returns:
            None
        """
        audio = AudioSegment.from_file(input_file_path, format="mp3")
        mid_seconds = audio[start_ms:end_ms]
        mid_seconds.export(output_file_path, format="mp3")
        return None

    @staticmethod
    def load_audio_as_mono_numpy(path: str, target_sample_rate: int = 16000) -> tuple[np.ndarray, int]:
        """
        Loads an audio file, resamples it, and mixes it down to a mono NumPy array.

        This utility prepares audio data for ML models (like Whisper) by ensuring the output is single-channel (mono)
        and matches the required sample rate. It handles stereo-to-mono conversion by averaging channels and flattens
        the result into a 1D array.

        Args:
            path (str): The file system path to the audio file (e.g., .wav, .mp3).
            target_sample_rate (int, optional): The desired sample rate in Hz. Default value is 16000 (standard for
            Whisper).

        Returns:
            tuple[np.ndarray, int]: A tuple containing:
                1. The audio waveform as a 1D NumPy array (shape: `(n_samples,)`).
                2. The final sample rate (int).

        Raises:
            RuntimeError: If torchaudio fails to load the file (e.g., corrupted file).
        """
        waveform, original_sr = torchaudio.load(path)

        if original_sr != target_sample_rate:
            resampler = T.Resample(original_sr, target_sample_rate)
            waveform = resampler(waveform)

        if waveform.shape[0] > 1:
            waveform = waveform.mean(dim=0, keepdim=True)

        audio_numpy = waveform.squeeze().numpy()
        return audio_numpy, target_sample_rate
