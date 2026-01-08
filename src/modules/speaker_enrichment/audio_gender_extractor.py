import torch
import torchaudio
from basic_gender_extractor import BasicGenderExtractor
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
        self.full_audio_path = ...  # TODO: add proper audio path
        self.temp_cut_audio_path = ...  # TODO: add proper cut audio path for saving temporary segments

    def predict_gender(self, video_path: str, segment: Segment) -> GenderExtractorReturnType | None:
        """
        This method is designed for many segments belonging to one speaker.
        """
        # create audio file from video
        AudioFileUtils.extract_audio_from_video(video_path, self.full_audio_path)

        # TODO: choose a couple of segments to analyze (if there are many)
        labels = {"female": 0, "male": 0}
        scores = {"max_female_score": -1, "max_male_score": -1}
        for segment in ...:  # in chosen segments
            # cut audio segment from full audio
            AudioFileUtils.cut_audio_segment(self.full_audio_path, self.temp_cut_audio_path,
                                             segment.start_h, segment.start_m, segment.start_s,
                                             segment.start_ms,
                                             segment.end_h, segment.end_m, segment.end_s,
                                             segment.end_ms)

            # get speech array from the cut audio file
            speech_array = self._prepare_speech_array_from_audio_file(self.temp_cut_audio_path)
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

            labels[label] += 1
            scores["max_" + label + "_score"] = max(scores["max_" + label + "_score"], score)

        final_label = max(labels, key=labels.get)  # to get the key with the highest value
        final_score = scores["max_" + final_label + "_score"]

        return {"label": final_label, "score": final_score}

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
