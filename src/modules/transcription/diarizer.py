from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
import torch
import torchaudio
from pyannote.audio.core.task import Specifications, Problem, Resolution
from pyannote.core import Annotation


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

    def diarize(self, audio_path: str) -> Annotation | None:
        """
        Performs speaker diarization for the provided audio file.

        This method loads the audio using torchaudio and passes the waveform through the Pyannote pipeline to
        identify "who spoke when". It returns a raw Annotation object containing the timeline of speaker turns.

        Args:
            audio_path (str): The file system path to the input audio file (e.g., .wav, .mp3).

        Returns:
            Annotation | None: A pyannote.core.Annotation object containing segments (start, end) and speaker labels
             (e.g., 'SPEAKER_00'), or None if the pipeline has not been successfully initialized.

        Raises:
            FileNotFoundError: If the audio_path does not exist.
            RuntimeError: If torchaudio fails to load the file.
            """
        if self.pipeline is None:
            return None

        try:
            with ProgressHook() as hook:
                waveform, sample_rate = torchaudio.load(audio_path)
                #default_parameters = self.pipeline.parameters(instantiated=True)
                #for param, value in default_parameters.items():
                    #print(f"{param}: {value}")

                diarization = self.pipeline({"waveform": waveform,
                                             "sample_rate": sample_rate},
                                            hook=hook,
                                            min_speakers=2,
                                            max_speakers=20)

                # post-process diarization result to increase its quality
                diarization = self._filter_short_segments(diarization)
                return diarization
        except Exception as e:
            print(f'Diarization error: {type(e)}: {e}')
            return None

    def _filter_short_segments(self, diarization: Annotation, min_duration_ms: int = 250) -> Annotation:
        """
        Filters out segments shorter than the specified duration to reduce noise for transcription.

        Very short segments (e.g., < 250 milliseconds by default) often contain non-speech sounds (breaths, clicks) or
        artifacts that can cause hallucinations, repetitive loops or even errors in the speech-to-text model
        (e.g. Whisper).

        Args:
            diarization (Annotation): The raw diarization result containing speaker segments.
            min_duration_ms (int, optional): The minimum duration threshold in milliseconds. Segments shorter than
            this value will be excluded. Defaults to 250.

        Returns:
            Annotation: A filtered Annotation object containing only the segments that meet the duration criteria.
        """
        cleaned_annotation = Annotation()
        for segment, _, speaker in diarization.itertracks(yield_label=True):
            if segment.duration > (min_duration_ms / 1000.0):
                cleaned_annotation[segment] = speaker
        return cleaned_annotation

