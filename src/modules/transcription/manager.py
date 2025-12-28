# main file for performing speech-to-text transcription and diarization
from llm_transcriber import LLMTranscriber


# TODO: implement
if __name__ == "__main__":
    transcriber = LLMTranscriber("/home/liza/Documents/Study/diploma/movies/shtolnia.avi",
                                 "../../../data/temporary_files/llm_transcript_shtolnia.txt")
    transcriber.write_transcript()