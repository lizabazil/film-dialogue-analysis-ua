import re
import os
from src.modules.nlp.udpipe_handler import UDPipeHandler
from src.modules.nlp.converters import UdpipeJsonToConlluConverter
from src.modules.nlp.nlp_aligner import NlpAligner
from src.utils.segment import Segment


class NLPUDPipeParser:
    """
    Read JSON file with UDPipe data, parses it and creates Segment objects from that data.
    """
    def __init__(self):
        self.udpipe_handler = UDPipeHandler()
        self.udpipe_json_to_conllu_converter = UdpipeJsonToConlluConverter()
        self.aligner = NlpAligner()

    def add_linguistic_features(self, segments: list[Segment], cached_json_path: str) -> list[Segment]:
        """
        Orchestrates the NLP enrichment pipeline for the provided speech segments.

        This method acts as a high-level coordinator that prepares the text, interfaces with  the UDPipe service,
        and integrates the results back into the domain objects.

        The process consists of four main steps:
        1. Preparation: Aggregates speech text from all segments into another variable to ensure UDPipe has
        full context for analysis.
        2. Processing: Sends the gathered data to the external UDPipe service via `UDPipeHandler`.
        3. Conversion: Transforms the raw JSON output into structured `conllu.TokenList`
           objects using `UdpipeJsonToConlluConverter`.
        4. Alignment: Maps the linear list of parsed sentences back to the specific time-coded segments using
        `NlpAligner`.

        Args:
            segments (list[Segment]): An ordered list of transcript segments to be processed.
            cached_json_path (str): Path to a pre-computed UDPipe JSON file. If such file exists, the UDPipe processing
             step is skipped, and data is loaded directly from this file. Otherwise, a fresh analysis is performed.
        Returns:
            list[Segment]: The list of segments, where each segment has its `.nlp_data` attribute has
             corresponding linguistic analysis from the UDPipe.
        """
        if not os.path.exists(cached_json_path):  # such JSON file with udpipe data does not exist, calling UDPipe
            # get the whole text for udpipe to the file
            input_for_udpipe = self._prepare_text_for_udpipe(segments)
            # send it to the udpipe
            self.udpipe_handler.process_text(input_for_udpipe, cached_json_path)

        # convert from udpipe json to conllu tokenList objects
        sentences = self.udpipe_json_to_conllu_converter.convert(cached_json_path)
        # align (enrich each segment .nlp_data field)
        segments_with_udpipe_data = self.aligner.align(segments, sentences)
        # return result enriched segments
        return segments_with_udpipe_data

    def _prepare_text_for_udpipe(self, segments: list[Segment]) -> str:
        """
        Extracts and formats speech text from the provided segments into a single string payload.
        This method aggregates the speech content and ensures that individual sentences are separated by newlines,
        which optimizes processing for the UDPipe tokenizer.

        Args:
            segments (list[Segment]): Input list of time-coded segments.

        Returns:
            str: A single string containing all extracted sentences, delimited by newline characters ('\n').
        """
        # using positive lookbehind
        regex_to_detect_end_of_sentence = re.compile(r"(?<=[.!?])\s+(?=[A-ZА-ЩЬЮЯҐЄІЇ])")
        res_str = ""
        for segment in segments:
            current_speech = regex_to_detect_end_of_sentence.sub("\n", segment.speech)
            res_str += (current_speech + "\n")
        return res_str
