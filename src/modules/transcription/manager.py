# main file for performing speech-to-text transcription and diarization
from llm_transcriber import LLMTranscriber
import yaml
from llm_transcript_parser import LLMTranscriptParser
from src.utils.video_utils import VideoUtils


def transcribe_movie(movie_path: str, output_file_path_str):
    with open("/home/liza/PycharmProjects/film-dialogue-analysis-ua/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    transcriber = LLMTranscriber(config)
    transcriber.write_full_transcript_to_the_file(movie_path, output_file_path_str)


def test_parsing_transcript(file_path: str, output_file_path: str, config: dict):
    merger = LLMTranscriptParser(config)
    merger.parse(file_path, output_file_path)


if __name__ == "__main__":
    # test_parsing_transcript(
    #     "/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/temporary_files/llm_transcript_shtolnia.txt",
    # "/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/temporary_files/parsed_llm_transcript_shtolnia.txt")

    # VideoUtils.get_subtitle_track_from_video("/home/liza/Downloads/Я, Ніна (2022) HMAX WEB-DL 1080p [UKR] [Hurtom].mkv",
    #                                          "/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/subtitles/Я_Ніна_2022.srt")

    with open("/home/liza/PycharmProjects/film-dialogue-analysis-ua/config.yaml", "r") as f:
        config = yaml.safe_load(f)
    transcriber = LLMTranscriber(config)

    movie_path = "/home/liza/Documents/Study/diploma/bilyj_ptach.mkv"  # ERROR
    write_transcript_to = "/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/temporary_files/llm_transcript_білий_птах_з_чорною_ознакою.txt"
    #transcriber.write_full_transcript_to_the_file(movie_path, write_transcript_to)

    movie_path = "/home/liza/Downloads/Taka_piznia_taka_tepla_osin_DVDRip_1080p_AI_Remaster.mp4"   # DONE
    write_transcript_to = "/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/temporary_files/llm_transcript_така_пізня_така_телпа_осінь.txt"
    #transcriber.write_full_transcript_to_the_file(movie_path, write_transcript_to)

    movie_path = "/home/liza/Documents/Study/diploma/Pryputni.mp4"   # ERROR
    write_transcript_to = "/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/temporary_files/llm_transcript_припутні.txt"
    #transcriber.write_full_transcript_to_the_file(movie_path, write_transcript_to)

    movie_path = "/home/liza/Downloads//home/liza/Documents/Study/diploma/huculka_ksenia.mkv"   # error
    write_transcript_to = "/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/temporary_files/llm_transcript_гуцулка_ксеня.txt"
    #transcriber.write_full_transcript_to_the_file(movie_path, write_transcript_to)

    movie_path = "/home/liza/Downloads/Evge.AKA.Homeward.2019.1080p.AMZN.WEB-DL.DD+5.1.H.264-Cinefeel.mkv"  # done
    write_transcript_to = "/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/temporary_files/llm_transcript_додому_2019.txt"
    transcriber.write_full_transcript_to_the_file(movie_path, write_transcript_to)

    movie_path = "/home/liza/Downloads/Трое(2025).mp4"  #  done
    write_transcript_to = "/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/temporary_files/llm_transcript_троє_2025.txt"
    transcriber.write_full_transcript_to_the_file(movie_path, write_transcript_to)

    movie_path = "/home/liza/Downloads/Такі красиві люди.mp4" #  done
    write_transcript_to = "/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/temporary_files/llm_transcript_такі_красиві_люди.txt"
    transcriber.write_full_transcript_to_the_file(movie_path, write_transcript_to)

    movie_path = "/home/liza/Downloads/KazkaProGroshi (mini).mp4" # done
    write_transcript_to = "/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/temporary_files/llm_transcript_казка_про_гроші.txt"
    transcriber.write_full_transcript_to_the_file(movie_path, write_transcript_to)

    # movie_path = "/home/liza/Downloads/Schoddenyk.Symona.Petliury.2018.Ukr.WEBDL.1080p.[Hurtom].mkv"
    # write_transcript_to = "/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/temporary_files/llm_transcript_schoddenyk_symona_petliury.txt"
    # transcriber.write_full_transcript_to_the_file(movie_path, write_transcript_to)
    #
    # movie_path = "/home/liza/Downloads/Slovo.House.Unfinished.Novel-WEBDL-1080p.mkv"
    # write_transcript_to = "/home/liza/PycharmProjects/film-dialogue-analysis-ua/data/temporary_files/llm_transcript_slovo_house_unfinished_novel.txt"
    # transcriber.write_full_transcript_to_the_file(movie_path, write_