import torch
import torchaudio
from src.modules.speaker_enrichment.basic_gender_extractor import BasicGenderExtractor
from transformers import AutoFeatureExtractor, AutoModelForAudioClassification
import numpy as np
from src.utils.audio_file_utils import AudioFileUtils
from src.utils.segment import Segment
from src.utils.gender_extractor_return_type import GenderExtractorReturnType


class AudioGenderExtractor(BasicGenderExtractor):
    """
    This class is responsible for predicting the gender by audio segments. It uses a pre-trained audio classification
    model.
    """

    def __init__(self, config: dict):
        super().__init__()
        self.model_name = config.get("speaker_enrichment", {}).get("audio_model_name", "")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.feature_extractor = AutoFeatureExtractor.from_pretrained(self.model_name)
        self.model = AutoModelForAudioClassification.from_pretrained(self.model_name).to(self.device)
        self.sampling_rate = 16000  # the model needs this specific sampling rate
        self.full_audio_path = "../../../data/temporary_files/full_audio_for_gender_extractor.mp3"
        self.custom_id_to_label = {"female": "woman", "male": "man"}
        self.last_given_video_path = ""

    def predict_gender(self, video_path: str, segment: Segment) -> GenderExtractorReturnType | None:
        """
        This method is designed for many segments belonging to one speaker.
        """
        # create audio file from video, if the video path is diffent from last added
        # this is done in order to improve performance
        if self.last_given_video_path != video_path:
            AudioFileUtils.extract_audio_from_video(video_path, self.full_audio_path)
            self.last_given_video_path = video_path

        speech_array = self._get_segment(segment.total_ms_start, segment.total_ms_end)

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
        custom_label = self.custom_id_to_label.get(label, label)

        return {"label": custom_label, "score": score}

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

    def _get_segment(self, start_ms: int, end_ms: int) -> np.ndarray:
        metadata = torchaudio.info(self.full_audio_path)
        orig_sr = metadata.sample_rate

        # get frames
        start_frame = int((start_ms / 1000) * orig_sr)
        num_frames = int(((end_ms - start_ms) / 1000) * orig_sr)

        waveform, sr = torchaudio.load(
            self.full_audio_path,
            frame_offset=start_frame,   # frame_offset is a jump into the file
            num_frames=num_frames,
            normalize=True
        )

        # convert to mono
        if waveform.shape[0] > 1:
            waveform = torch.mean(waveform, dim=0, keepdim=True)

        if sr != self.sampling_rate:
            resampler = torchaudio.transforms.Resample(sr, self.sampling_rate)
            waveform = resampler(waveform)

        return waveform.squeeze().numpy()
