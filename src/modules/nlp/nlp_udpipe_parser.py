from src.modules.nlp.udpipe_handler import UDPipeHandler
from src.modules.nlp.converters import UdpipeJsonToConlluConverter
from src.modules.nlp.nlp_aligner import NlpAligner
from src.utils.segment import Segment
from src.utils.file_utils import FileUtils


class NLPUDPipeParser:
    """
    Read JSON file with UDPipe data, parses it and creates Segments objects from that data.
    """
    def __init__(self, json_udpipe_file_name: str):
        """
        Args:
            json_udpipe_file_name: Destination for the JSON file to store UDPipe output.
        """
        self.udpipe_handler = UDPipeHandler()
        self.udpipe_json_to_conllu_converter = UdpipeJsonToConlluConverter()
        self.aligner = NlpAligner()
        self.json_udpipe_file_name = json_udpipe_file_name  # this file will be containing UDPipe result
        self.temp_file_for_only_text = "../../../temp_text_file.txt"  # TODO: improve

    def enrich_segments(self, segments: list[Segment]) -> list[Segment]:
        """
        Orchestrates the NLP enrichment pipeline for the provided speech segments.

        This method acts as a high-level coordinator that prepares the text, interfaces with  the UDPipe service,
        and integrates the results back into the domain objects.

        The process consists of four main steps:
        1. Preparation: Aggregates speech text from all segments into another text file to ensure UDPipe has
        full context for analysis.
        2. Processing: Sends the created file to the external UDPipe service via `UDPipeHandler`.
        3. Conversion: Transforms the raw JSON output into structured `conllu.TokenList`
           objects using `UdpipeJsonToConlluConverter`.
        4. Alignment: Maps the linear list of parsed sentences back to the specific time-coded segments using
        `NlpAligner`.

        Args:
            segments (list[Segment]): An ordered list of transcript segments to be processed.
        Returns:
            list[Segment]: The input list of segments, where each segment has its `.nlp_data` attribute has
             corresponding linguistic analysis from the UDPipe.
        """
        self._delete_files_to_write_new_data()

        # get the whole text for udpipe to the file
        self._prepare_text_for_udpipe(segments)
        # send it to the udpipe
        self.udpipe_handler.process_file(self.temp_file_for_only_text, self.json_udpipe_file_name)
        # convert from udpipe json to conllu tokenList objects
        sentences = self.udpipe_json_to_conllu_converter.convert(self.json_udpipe_file_name)
        # align (enrich each segment .nlp_data field)
        segments_with_udpipe_data = self.aligner.align(segments, sentences)
        # return result enriched segments
        return segments_with_udpipe_data

    def _prepare_text_for_udpipe(self, segments: list[Segment]) -> None:
        with open(self.temp_file_for_only_text, "w") as f:
            for segment in segments:
                f.write(segment.speech)
                f.write("\n")
        return None

    def _delete_files_to_write_new_data(self):
        FileUtils.delete_file(self.temp_file_for_only_text)
        FileUtils.delete_file(self.json_udpipe_file_name)
        return None
