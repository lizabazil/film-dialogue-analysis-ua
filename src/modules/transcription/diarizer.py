from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
import torch
import torchaudio
from pyannote.audio.core.task import Specifications, Problem, Resolution


class PyannoteDiarizer:
    def __init__(self, hf_token):
        try:
            torch.serialization.add_safe_globals([torch.torch_version.TorchVersion])
            torch.serialization.add_safe_globals([
                torch.torch_version.TorchVersion,
                Specifications,
                Problem,
                Resolution
            ])
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=hf_token
            )
            self.device = torch.device(
                "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
            self.pipeline.to(self.device)
        except Exception as e:
            print(f"CRITICAL ERROR initializing pipeline: {e}")
            self.pipeline = None

    def diarize(self, audio_path: str):
        if self.pipeline is None:
            return None

        try:
            with ProgressHook() as hook:
                waveform, sample_rate = torchaudio.load(audio_path)
                default_parameters = self.pipeline.parameters(instantiated=True)
                #for param, value in default_parameters.items():
                    #print(f"{param}: {value}")

                diarization = self.pipeline({"waveform": waveform,
                                             "sample_rate": sample_rate},
                                            hook=hook,
                                            min_speakers=2,
                                            max_speakers=20)
                return diarization
        except Exception as e:
            print(f'Diarization error: {type(e).__name__} - {e}')
            return None
