import os.path

from src.modules.transcription.diarizer import PyannoteDiarizer
from src.modules.transcription.diarization_io import DiarizationIO
from src.modules.transcription.whisper_transcriber import WhisperTranscriber
from src.modules.transcription.transcript_io import TranscriptIO
from src.modules.preprocessing.whisper_transcript_cleaner import WhisperTranscriptCleaner
from src.modules.preprocessing.normalizers import SegmentNormalizer
from src.modules.nlp.nlp_udpipe_parser import NLPUDPipeParser
from src.modules.speaker_enrichment.gender_identifier import GenderEnricher
from src.utils.audio_file_utils import AudioFileUtils
from src.utils.time_utils import TimeUtils
import yaml
from pathlib import Path
from src.utils.segment import Segment
from src.modules.analysis.engine import AnalysisEngine
from pyannote.core import Annotation


class VideoPipeline:
    def __init__(self, config: dict):
        self.config = config
        relative_working_path = self.config.get("storage", {}).get("working_files_dir", "data/working_files")

        # with current working directory
        self.output_dir = Path.cwd() / relative_working_path
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._diarizer = None
        self._transcriber = None

        self.transcript_io_manager = TranscriptIO()
        self.diarization_io = DiarizationIO()
        self.cleaner = WhisperTranscriptCleaner()
        self.normalizer = SegmentNormalizer()
        self._nlp_udpipe_parser = None
        self._gender_enricher = None
        self.analysis_engine = AnalysisEngine()

    @property
    def diarizer(self):
        if self._diarizer is None:
            self._diarizer = PyannoteDiarizer(self.config)
        return self._diarizer

    def unload_diarizer(self):
        if self._diarizer is not None:
            self._diarizer.cleanup()
            self._diarizer = None

    @property
    def transcriber(self):
        if self._transcriber is None:
            self._transcriber = WhisperTranscriber(self.config)
        return self._transcriber

    def unload_transcriber(self):
        if self._transcriber is not None:
            self._transcriber.cleanup()
            self._transcriber = None

    @property
    def gender_enricher(self):
        if self._gender_enricher is None:
            self._gender_enricher = GenderEnricher(self.config)
        return self._gender_enricher

    @property
    def nlp_udpipe_parser(self):
        if self._nlp_udpipe_parser is None:
            self._nlp_udpipe_parser = NLPUDPipeParser()
        return self._nlp_udpipe_parser

    @staticmethod
    def load_config(path: str) -> dict:
        with open(path, "r") as f:
            config = yaml.safe_load(f)
        return config

    def run(self, video_path: str):
        # full pipeline
        # diarization
        paths = self._generate_paths(video_path)
        full_audio_path = paths.get("full_audio")
        AudioFileUtils.extract_audio_from_video(video_path, full_audio_path)

        annotation = self.diarizer.diarize(full_audio_path)
        self.unload_diarizer()

        # save checkpoint with diarization
        self.diarization_io.save_diarization(annotation, f"{self.output_dir}/diarization.txt")
        # whisper
        segments_after_whisper = self._generate_transcript_from_annotation(annotation, full_audio_path)
        self.unload_transcriber()

        # save checkpoint: save raw (not cleaned) transcript into txt file
        self.transcript_io_manager.save(segments_after_whisper, paths.get("transcript"))
        # and then:
        nlp_and_gender_annotated_segments = self._process_text_pipeline(segments_after_whisper, video_path,
                                                                        paths.get("udpipe"))

        analysis_report = self.analysis_engine.run_full_analysis(nlp_and_gender_annotated_segments, video_path)
        return analysis_report

    def _generate_transcript_from_annotation(self, annotation: Annotation, full_audio_path: str) -> list[Segment]:
        full_audio_numpy, sr = AudioFileUtils.load_audio_as_mono_numpy(full_audio_path)

        segments = []
        for segment, _, speaker in annotation.itertracks(yield_label=True):
            start_sample = int(segment.start * sr)
            end_sample = int(segment.end * sr)

            if end_sample > len(full_audio_numpy):
                end_sample = len(full_audio_numpy)

            audio_segment_array = full_audio_numpy[start_sample:end_sample]

            start_h, start_m, start_s, start_ms = TimeUtils.convert_seconds_to_proper_format(segment.start)
            end_h, end_m, end_s, end_ms = TimeUtils.convert_seconds_to_proper_format(segment.end)

            speech = self.transcriber.get_transcription(audio_segment_array, sample_rate=sr)
            segment = Segment(speaker, start_h, start_m, start_s, start_ms,
                              end_h, end_m, end_s, end_ms, speech.strip())
            segments.append(segment)

        return segments

    def run_with_existing_transcript(self, transcript_path: str, video_path: str, udpipe_cache_file_path: str = None):
        if not os.path.exists(transcript_path):
            raise FileNotFoundError(f"Transcript file {transcript_path} can not be found.")

        parsed_segments_from_transcript, with_gender_notes = self.transcript_io_manager.parse(transcript_path)
        # add genders in case it is not there yet
        nlp_data_and_gender_annotated_segments = (
            self._process_text_pipeline(parsed_segments_from_transcript, video_path, udpipe_cache_file_path,
                                        with_genders_already=with_gender_notes, clean_replicas=False))

        analysis_report = self.analysis_engine.run_full_analysis(nlp_data_and_gender_annotated_segments, video_path)
        return analysis_report

    def _process_text_pipeline(self, segments: list, video_path: str, udpipe_file_path: str | None,
                               with_genders_already: bool = False, clean_replicas: bool = True) -> list[Segment]:
        """

        Args:
            segments: Segments without 'nlp_data' and 'gender' fields.
            video_path: Path to the original video.
            udpipe_file_path: Path to the UDPipe JSON file. If such file does not exist, the UDPipe service is called.
            Otherwise, the cache file is used.

        Returns:
            list[Segment]: Final segments with gender notes and nlp data.
        """
        paths = self._generate_paths(video_path)
        # udpipe file_path may not exist. if it exists, udpipe won't run its pipeline again
        # if it does not exist, then udpipe will run its pipeline and save its result to the given file

        # 1. cleaner
        # if there was existing transcript - then no cleaning here
        if clean_replicas:
            segments = self.cleaner.clean(segments)
        self.transcript_io_manager.save(segments, paths.get("transcript"))

        # 2. normalizer
        normalized_segments = self.normalizer.normalize(segments)
        # 3. NLP udpipe parser
        if udpipe_file_path is None or not os.path.exists(udpipe_file_path):
            udpipe_file_path = paths.get("udpipe")

        segments_with_linguistic_features = self.nlp_udpipe_parser.add_linguistic_features(normalized_segments,
                                                                                           udpipe_file_path)

        # 4. gender enricher and saving to the json lines file
        if not with_genders_already:
            gender_annotated_segments = self.gender_enricher.annotate_segments(video_path,
                                                                               segments_with_linguistic_features,
                                                                               paths.get("final_jsonl"))
            return gender_annotated_segments
        else:
            return segments_with_linguistic_features

    def _generate_paths(self, video_source_path: str) -> dict:
        """
        Generates output file paths for pipeline checkpoints and final results.

        This method constructs paths based on the video filename stem and the configured output directory. It ensures
        consistent naming for all intermediate artifacts (audio, cache, raw text).

        Args:
            video_source_path (str): The file system path to the input video file.

        Returns:
            dict: A dictionary containing the following path objects (or strings):
                - 'udpipe': Path for the UDPipe linguistic analysis cache (JSON).
                - 'transcript': Path for the raw Whisper transcription (TXT).
                - 'final_jsonl': Path for the final annotated dataset with gender info.
                - 'full_audio': Path for the audio track extracted from the video.
        """
        video_source_path = Path(video_source_path)
        stem = video_source_path.stem
        return {
            # for saving UDPipe result
            "udpipe": self.output_dir / f"{stem}_udpipe_cache.json",
            # saving raw transcript file
            "transcript": self.output_dir / f"{stem}_transcript.txt",
            # for saving result to the final json lines
            "final_jsonl": self.output_dir / f"{stem}_final.jsonl",
            # for audio path (made from video)
            "full_audio": self.output_dir / f"{stem}_full_audio.mp3",
            "parsed_transcript": self.output_dir / f"{stem}_parsed_transcript.txt"
        }
