import torch
import torchaudio
from basic_gender_extractor import BasicGenderExtractor
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification
import numpy as np
import subprocess


class AudioGenderExtractor(BasicGenderExtractor):
    def __init__(self, config: dict, video_path: str):
        super().__init__()
        self.video_path = video_path
        self.model_name = config.get("speaker_enrichment", {}).get("audio_model_name", "")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(self.model_name)
        self.model = AutoModelForAudioClassification.from_pretrained(self.model_name).to(self.device)
        self.sampling_rate = 16000   # the model needs this specific sampling rate
        self.audio_path = ...  # TODO: add proper audio path

        # create audio file from video
        self._convert_to_audio_file()

    def predict_gender(self, segments: list) -> dict | None:
        # TODO: choose a couple of segments to analyze (if there are many)
        best_label = None
        best_score = -1
        for segment in ...:   # in chosen segments
            speech_array = self._prepare_speech_array_from_audio_file(...)  # TODO: provide valid audio file path
            inputs = self.feature_extractor(
                speech_array,
                sampling_rate=self.sampling_rate,
                return_tensors="pt",
            )
            inputs = inputs.to(self.device)
            logits, probs = self._use_model_to_get_prediction(inputs)

            pred_id = torch.argmax(logits, dim=-1).item()
            score = probs[0][pred_id].item()
            label = self.model.config.id2label[pred_id]

            if score > best_score:
                best_score = score
                best_label = label
        return {"label": best_label, "score": best_score}

    def _use_model_to_get_prediction(self, inputs) -> tuple:
        """
        Uses the audio classification model to get prediction logits and probabilities.
        """
        with torch.no_grad():
            logits = self.model(**inputs).logits
            probs = torch.nn.functional.softmax(logits, dim=-1)
        return logits, probs

    def _prepare_speech_array_from_audio_file(self, audio_path: str) -> np.ndarray:
        """
        Loads an audio file and prepares a speech array suitable for audio model input.
        """
        speech_array, sr = torchaudio.load(audio_path)
        if speech_array.shape[0] > 1:
            speech_array = torch.mean(speech_array, dim=0, keepdim=True)

        # resample the sampling rate if needed (to match model's requirements)
        if sr != self.sampling_rate:
            transform = torchaudio.transforms.Resample(orig_freq=sr, new_freq=self.sampling_rate)
            speech_array = transform(speech_array)
            sr = self.sampling_rate

        speech_array = speech_array.squeeze().numpy()
        return speech_array

    def _convert_to_audio_file(self) -> None:
        """
        Converts the video file to an audio file using ffmpeg.
        """
        command = [
            "ffmpeg",
            "-i", self.video_path,
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ar', '16000',   # to 16 kHz
            '-ac', '1',  # to one audio channel
            '-y',   # overwrite output file if exists
            self.audio_path
        ]
        try:
            subprocess.run(command, check=True)
        except Exception as e:
            print(f"Error during audio extraction: {e}")
        return None
