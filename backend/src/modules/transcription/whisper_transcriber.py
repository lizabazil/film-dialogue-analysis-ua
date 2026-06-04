import numpy as np
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from typing import Union
import gc


class WhisperTranscriber:
    """
    Class for performing speech-to-text transcription using given Whisper model.
    """
    def __init__(self, config: dict):
        """
        Args:
            config (dict): Dictionary with configuration data.
        """
        self.device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.model_id = config.get("speech_to_text_model", {}).get("whisper_model_name", "openai/whisper-large-v3")
        self.target_language = config.get("speech_to_text_model", {}).get("target_language", "uk")
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_id, torch_dtype=self.torch_dtype, low_cpu_mem_usage=True,
            use_safetensors=True
        )

        self.model.to(self.device)

        self.processor = AutoProcessor.from_pretrained(self.model_id)

        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=self.processor.tokenizer,
            feature_extractor=self.processor.feature_extractor,
            dtype=self.torch_dtype,
            device=self.device,
        )

    def get_transcription(self, audio_input: Union[str, np.ndarray], sample_rate: int = 16000) -> str:
        """
        Get text from given audio input (file path or raw numpy array).
        """
        if isinstance(audio_input, np.ndarray):
            prediction_input = {"raw": audio_input, "sampling_rate": sample_rate}
        else:
            prediction_input = audio_input

        result = self.pipe(
            prediction_input,
            generate_kwargs={
                "task": "transcribe",
                "language": self.target_language,
            },
        )

        return result["text"]

    def cleanup(self):
        if hasattr(self, 'pipe'):
            del self.pipe

        if hasattr(self, 'model'):
            self.model.to("cpu")
            del self.model

        if hasattr(self, 'processor'):
            del self.processor

        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
