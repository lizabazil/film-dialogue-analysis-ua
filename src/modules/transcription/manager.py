# main file for performing speech-to-text transcription and diarization
from llm_transcriber import LLMTranscriber
import yaml
from llm_transcript_merger import LLMTranscriptMerger


def transcribe_movie(movie_path: str, output_file_path_str):
    with open("/home/liza/PycharmProjects/film-dialogue-analysis-ua/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    transcriber = LLMTranscriber(movie_path, config,
                                 output_file_path_str)
    transcriber.write_full_transcript_to_the_file()


def test_parsing_transcript(file_path: str, output_file_path: str):
    merger = LLMTranscriptMerger(8, 1)
    merger.read_raw_transcript_file_from_llm_and_set_proper_format(file_path, output_file_path)


if __name__ == "__main__":
    # test_parsing_transcript(
    #     "/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/temporary_files/llm_transcript_shtolnia.txt",
    # "/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/temporary_files/parsed_llm_transcript_shtolnia.txt")

    movie_path = "/home/liza/Documents/Study/diploma/movies/when-the-trees-fall.mkv"
    write_transcript_to = "/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/temporary_files/llm_transcript_when_the_trees_fall.txt"
    transcribe_movie(movie_path, write_transcript_to)
