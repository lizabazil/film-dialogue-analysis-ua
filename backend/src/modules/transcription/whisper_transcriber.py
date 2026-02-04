"""
File for transcribing audio using the OpenAI Whisper model.
"""
import numpy as np
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from typing import Union


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
        #self.model_id = config.get("speech_to_text_model", {}).get("whisper_model_name", "openai/whisper-large-v3")
        self.model_id = "openai/whisper-large-v3-turbo" #"openai/whisper-base" #
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
            #return_timestamps=True,
        )
        print(f"Whisper init done for {self.model_id}")

    def get_whisper_transcription(self, audio_path: str) -> str:
        """
        Get text from given audio file.

        Args:
            audio_path (str): Path to audio file.
        Returns:
             str: Textual result from Whisper model.
        """
        result = self.pipe(audio_path,
                           generate_kwargs={
                               "task": "transcribe",
                               "language": "ukrainian",
                           },
                           )

        transcription = result['text']
        return transcription

    def get_whisper_transcription_from_array(self, audio_input: Union[str, np.ndarray], sample_rate: int = 16000) -> str:
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
                "language": "ukrainian",
            },
        )

        return result['text']
