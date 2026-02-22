# a class that can convert different formats (SRT reference and the result from LLM) into a single list of
# EvalSegment objects
import json

from src.utils.segment import Segment
from src.evaluation.schemas import EvalSegment
from abc import ABC, abstractmethod
from srt_transcript_parser import SrtTranscriptParser


class BaseParser(ABC):
    @abstractmethod
    def parse(self, file_path: str) -> list[EvalSegment]:
        pass


class JSONParser(BaseParser):
    def parse(self, file_path: str) -> list[EvalSegment]:
        """
        Parses JSONL file.
        Args:
            file_path:

        Returns:

        """
        segments = []
        with open(file_path, "r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    segment = EvalSegment(
                        start_ms=data.get("total_ms_start", 0),
                        end_ms=data.get("total_ms_end", 0),
                        speech=data.get("speech", ""),
                        speaker_id=data.get("speaker_id", ""),
                        gender=data.get("gender", ""),
                        lemmas=[]  # will be completed later
                    )

                    segments.append(segment)
                except json.JSONDecodeError as e:
                    print(f"Error in the line: {line_number} ({line}): {e}")
        return segments


class ParserFactory:
    @staticmethod
    def get_parser(file_path: str) -> BaseParser:
        if file_path.endswith(".srt"):
            return SrtTranscriptParser()
        if file_path.endswith(".jsonl"):
            return JSONParser()


# def convert_to_evaluation_segment(original_segment: Segment) -> EvalSegment:
#     start_ms = original_segment.total_ms_start
#     end_ms = original_segment.total_ms_end
#     lemmas = []
#
#     if original_segment.nlp_data:
#         for sentence in original_segment.nlp_data:
#             for token in sentence:
#                 lemma = token.get("lemma")
#                 upos = token.get("upos")
#                 if lemma and upos != "PUNCT":
#                     lemmas.append(lemma)
#
#     return EvalSegment(
#         start_ms,
#         end_ms,
#         speech=original_segment.speech,
#         speaker_id=original_segment.speaker_id,
#         gender=original_segment.gender,
#         lemmas=lemmas
#     )
