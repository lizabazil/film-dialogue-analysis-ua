"""
File for transcribing audio using the OpenAI Whisper model.
"""
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline


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
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_id, torch_dtype=self.torch_dtype, low_cpu_mem_usage=True,
            use_safetensors=True
        )

        self.model.to(self.device)

        processor = AutoProcessor.from_pretrained(self.model_id)

        self.pipe = pipeline(
            "automatic-speech-recognition",
            model=self.model,
            tokenizer=processor.tokenizer,
            feature_extractor=processor.feature_extractor,
            torch_dtype=self.torch_dtype,
            device=self.device,
            return_timestamps=True,
        )

    def get_whisper_transcription(self, audio_path):
        result = self.pipe(audio_path,
                           generate_kwargs={
                               "task": "transcribe",
                               "language": "ukrainian",
                           },
                           )

        transcription = result['text']
        return transcription
