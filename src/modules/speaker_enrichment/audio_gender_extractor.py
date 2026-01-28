import torch
import torchaudio
from src.modules.speaker_enrichment.basic_gender_extractor import BasicGenderExtractor
import numpy as np
from src.utils.audio_file_utils import AudioFileUtils
from src.utils.segment import Segment
from src.utils.gender_extractor_return_type import GenderExtractorReturnType
from transformers import Wav2Vec2ForSequenceClassification, Wav2Vec2FeatureExtractor


class AudioGenderExtractor(BasicGenderExtractor):
    """
    This class is responsible for predicting the gender by audio segments. It uses a pre-trained audio classification
    model.
    """

    def __init__(self, config: dict):
        super().__init__()
        self.model_name = config.get("speaker_enrichment", {}).get("audio_model_name", "")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.sampling_rate = 16000  # the model needs this specific sampling rate
        self.full_audio_path = "../../../data/temporary_files/full_audio_for_gender_extractor.mp3"
        self.custom_id_to_label = {"female": "woman", "male": "man"}
        self.last_given_video_path = ""

        print(f"Loading Audio Gender Model on {self.device}...")

        try:
            self.processor = Wav2Vec2FeatureExtractor.from_pretrained(self.model_name)
            self.model = Wav2Vec2ForSequenceClassification.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            print(f"Failed to load model: {e}")
            raise e

        self.id2label = {
            0: "woman",
            1: "man"
        }

    def predict_gender(self, video_path: str, segment: Segment) -> GenderExtractorReturnType | None:
        try:
            if self.last_given_video_path != video_path:
                print(f"Extracting full audio from video: {video_path}...")

                AudioFileUtils.extract_audio_from_video(video_path, self.full_audio_path)
                self.last_given_video_path = video_path

            start_sec = segment.total_ms_start / 1000.0
            end_sec = segment.total_ms_end / 1000.0
            duration = end_sec - start_sec

            if duration < 0.1:
                return None

            info = torchaudio.info(self.full_audio_path)
            orig_sr = info.sample_rate

            frame_offset = int(start_sec * orig_sr)
            num_frames = int(duration * orig_sr)

            if num_frames <= 0:
                return None

            # loading a segment
            waveform, _ = torchaudio.load(
                self.full_audio_path,
                frame_offset=frame_offset,
                num_frames=num_frames
            )

            if waveform.shape[0] > 1:
                speech = waveform.mean(dim=0)
            else:
                speech = waveform.squeeze(0)

            speech = speech.numpy()

            if len(speech) == 0:
                return None

            inputs = self.processor(
                speech,
                sampling_rate=self.sampling_rate,
                return_tensors="pt",
                padding=True
            )

            inputs = {key: val.to(self.device) for key, val in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=1).squeeze()

                if probs.dim() == 0:
                    probs = torch.tensor([1.0 - probs, probs]).to(self.device)

                predicted_id = torch.argmax(probs).item()
                confidence_score = probs[predicted_id].item()

            predicted_label = self.id2label.get(predicted_id, "unknown")

            return {
                "label": predicted_label,
                "score": round(confidence_score, 4)
            }

        except Exception as e:
            print(f"Error: {e}")
            return None
