# this file will be using all methods for identifying the gender of the speaker
from src.modules.speaker_enrichment.audio_gender_extractor import AudioGenderExtractor
from src.modules.speaker_enrichment.visual_gender_extractor import VisualGenderExtractor
from src.modules.speaker_enrichment.text_gender_extractor import TextGenderExtractor
from src.utils.segment import Segment
from src.modules.post_processing.normalizers import SegmentNormalizer
from collections import Counter
import json
from src.utils.gender_extractor_return_type import GenderExtractorReturnType


class GenderEnricher:
    """
    Main class which uses different approaches to detect the gender of the speaker.
    """
    def __init__(self, config: dict):
        self.audio_gender_extractor = AudioGenderExtractor(config)
        self.visual_gender_extractor = VisualGenderExtractor(config)
        self.text_gender_extractor = TextGenderExtractor()

        self.segment_normalizer = SegmentNormalizer()

    def annotate_segments(self, video_path: str, all_segments: list[Segment], json_lines_file_path: str | None) -> (
            list)[Segment]:
        """
        Segments by the same speaker may not be already joined (especially if the pause is significant).
        Args:
            video_path:
            all_segments:
            json_lines_file_path:

        Returns:

        """
        next_index_to_process = 0
        total_segments = len(all_segments)
        gender_annotated_segments = []

        while next_index_to_process < total_segments:
            neighbors = self._get_neighboring_segments(all_segments, target_segment_index=next_index_to_process)
            same_speaker_segments, next_index_to_process = self._collect_segments_of_same_speaker(all_segments,
                                                                                          target_segment_index=
                                                                                          next_index_to_process)

            next_index_to_process += 1

            # sort, so the segments are in a proper order (sort by the start time)
            same_speaker_segments = self._sort_segments_by_time_start(same_speaker_segments)
            neighbors = self._sort_segments_by_time_start(neighbors)
            same_speaker_segments_into_one = self.segment_normalizer.merge_close_segments(
                segments=same_speaker_segments, gap_duration_in_seconds=float('inf'))
            if len(same_speaker_segments_into_one) != 1:
                raise ValueError(f"Size of segments by the same speaker list MUST 1, but it's current value is "
                                 f"{len(same_speaker_segments_into_one)}")

            the_whole_segment_to_analyze = same_speaker_segments_into_one[0]

            audio_result = self.audio_gender_extractor.predict_gender(video_path,
                                                                      segment=the_whole_segment_to_analyze)
            visual_result = self.visual_gender_extractor.predict_gender(video_path, segment=the_whole_segment_to_analyze)
            text_result = self.text_gender_extractor.predict_gender(target_segment=the_whole_segment_to_analyze,
                                                                    neighboring_segments=neighbors)

            final_gender_decision = self._resolve_gender_conflict((audio_result.get("label") if audio_result is not None else None),
                                                                  (visual_result.get("label") if visual_result is not None else None),
                                                                  (text_result.get("label", None) if text_result is not None else None))

            # annotate all the segments by the same speaker
            for s in same_speaker_segments:
                if final_gender_decision is not None:
                    s.gender = final_gender_decision
                gender_annotated_segments.append(s)
                # convert segment to dict structure and save to the json lines file
                dict_segment = s.to_dict()
                self._write_segment_data_to_json_lines_file(json_lines_file_path, dict_segment)

                # for debugging
                self._write_segment_data_to_json_lines_file(json_lines_file_path, {"audio": audio_result if audio_result is not None else None})
                self._write_segment_data_to_json_lines_file(json_lines_file_path, {"visual": visual_result if visual_result is not None else None})
                self._write_segment_data_to_json_lines_file(json_lines_file_path, {"text": text_result if text_result is not None else None})

        return gender_annotated_segments

    def _write_segment_data_to_json_lines_file(self, file_path: str, segment_dict: dict) -> None:
        """
        Appends a single dictionary as a JSON line to the specified file.

        This method opens the file in append mode ('a'), serializes the dictionary to a JSON string, and writes it
        followed by a newline character.
        It uses ensure_ascii=False to preserve non-ASCII characters (e.g., Cyrillic) in their original form.

        Args:
            file_path (str): The absolute or relative path to the target .jsonl file.
            segment_dict (dict): A dictionary containing the segment data. Must be JSON-serializable.

        Returns:
            None
        """
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(segment_dict, ensure_ascii=False) + "\n")
        return None

    def _resolve_gender_conflict(self,
                                 audio: GenderExtractorReturnType | None,
                                 visual: GenderExtractorReturnType | None,
                                 text: GenderExtractorReturnType | None) -> str | None:
        """
        Makes decision between conflicting gender predictions from audio, visual, and textual sources.

        The resolution logic follows a hierarchy based on data availability:
        1. If text result is available and its confidence equals to 1.0, then the final result will be taken directly
         from the text result, as it's highly reliable information.
        2. Three sources available: Uses majority voting (2 vs 1) or consensus.
        3. Two sources available:
            - If they agree: Returns the common prediction.
            - If they disagree: Follows the priority **Text > Audio > Visual**.
        4. One source available: Returns the single available prediction.

        Args:
            audio (str | None): Gender predicted from audio analysis (e.g., 'man', 'woman').
            visual (str | None): Gender predicted from visual analysis.
            text (str | None): Gender inferred from text/linguistic analysis.

        Returns:
            str | None: The resolved gender label, or None if no predictions are provided.
        """
        results = [res for res in [audio, visual, text] if res is not None]
        if not results:
            return None

        # if the confidence score of text result equals 1.0 -> immediately choose its result and the final
        if text is not None and text.get("score") == 1.0:
            return text.get("label")

        only_labels = [label.get("label") for label in results]
        if len(only_labels) == 1:
            return only_labels[0]

        if len(results) == 3:  # available all the results
            counts = Counter(only_labels)
            most_common, count = counts.most_common(1)[0]
            return most_common

        # priority goes like this: text > audio > visual
        if text is not None:
            return text.get("label")
        if audio is not None:
            return audio.get("label")
        return visual.get("label")

    def _collect_segments_of_same_speaker(self, all_segments: list[Segment], target_segment_index: int) -> (
            tuple)[list[Segment], int]:
        """
        Collects the segments, which have the same speaker Id, as given target segment.

        IMPORTANT: this method includes the target segment in the returned list of segments.
        Args:
            all_segments: Full list of segments.
            target_segment_index: The index of the target segment.

        Returns:
            list[Segment]: List of neighboring segments, whose speaker Ids equal to the target segment's speaker Id.
        """
        max_index_of_the_target_speaker = target_segment_index

        if target_segment_index < 0 or target_segment_index >= len(all_segments):
            return [], target_segment_index
        result_segments = [all_segments[target_segment_index]]

        target_segment_speaker_id = all_segments[target_segment_index].speaker_id
        total_segments = len(all_segments)

        local_index = target_segment_index - 1
        if local_index >= 0:
            # to the left
            curr_segment = all_segments[local_index]
            while curr_segment.speaker_id == target_segment_speaker_id:
                result_segments.append(curr_segment)
                local_index -= 1
                if local_index < 0:
                    break
                curr_segment = all_segments[local_index]

        # to the right
        local_index = target_segment_index + 1
        if local_index < total_segments:
            curr_segment = all_segments[local_index]
            while curr_segment.speaker_id == target_segment_speaker_id:
                result_segments.append(curr_segment)
                max_index_of_the_target_speaker = local_index

                local_index += 1
                if local_index >= total_segments:
                    break
                curr_segment = all_segments[local_index]
                #max_index_of_the_target_speaker = local_index

        return result_segments, max_index_of_the_target_speaker

    def _sort_segments_by_time_start(self, segments: list[Segment]) -> list[Segment]:
        """
        Sorts a list of segments chronologically based on their absolute start time.
        This operation is **not in-place**. It creates and returns a new list using the built-in `sorted()` function,
        leaving the original `segments` list unmodified.

        Args:
            segments (list[Segment]): The list of Segment objects to be sorted.

        Returns:
            list[Segment]: A new list containing the segments sorted in ascending order by their `total_ms_start`
            attribute.
                """
        res = sorted(segments, key=lambda x: x.total_ms_start)
        return res

    def _get_neighboring_segments(self, all_segments: list[Segment], target_segment_index: int) -> list[Segment]:
        """
        Retrieves the immediate adjacent segments (previous and next) relative to the target segment.
       It safely handles list boundaries (first and last elements).

        Args:
            all_segments (list[Segment]): The complete ordered list of transcript segments.
            target_segment_index (int): The index of the segment for which neighbors are required.

        Returns:
            list[Segment]: A list of existing neighboring segments. If there is a neighbor which have several segments
            in a row, then all of those segments will be returned.
        """
        total_all_segments = len(all_segments)

        if target_segment_index < 0 or target_segment_index >= total_all_segments:
            return []

        neighboring_segments = []
        before_segment = None
        after_segment = None

        target_segment_speaker_id = all_segments[target_segment_index].speaker_id
        if target_segment_index > 0:
            before_segment = all_segments[target_segment_index - 1]
            local_index = target_segment_index - 2

            while before_segment.speaker_id == target_segment_speaker_id and local_index >= 0:
                before_segment = all_segments[local_index]
                local_index -= 1

            # get segments from the same neighbor
            if before_segment and before_segment.speaker_id != target_segment_speaker_id:
                neighboring_segments.append(before_segment)

                the_same_neighbor_segments = self._get_neighboring_segments_by_the_same_speaker(all_segments,
                                                                                                local_index + 1)
                if the_same_neighbor_segments:
                    neighboring_segments.extend(the_same_neighbor_segments)

        if target_segment_index < len(all_segments) - 1:
            after_segment = all_segments[target_segment_index + 1]
            local_index = target_segment_index + 2
            while after_segment.speaker_id == target_segment_speaker_id and local_index < total_all_segments:
                after_segment = all_segments[local_index]
                local_index += 1

            # get segments form the same neighbor
            if after_segment and after_segment.speaker_id != target_segment_speaker_id:
                neighboring_segments.append(after_segment)
                the_same_neighbor_segments = self._get_neighboring_segments_by_the_same_speaker(all_segments, local_index - 1)

                if the_same_neighbor_segments:
                    neighboring_segments.extend(the_same_neighbor_segments)

        return neighboring_segments

    def _get_neighboring_segments_by_the_same_speaker(self, all_segments: list[Segment], target_segment_index: int) -> list[Segment]:
        """
        Retrieves a continuous block of segments belonging to the same speaker surrounding the target segment.

        This method scans left and right from the target index and collects all consecutive segments
        that share the same `speaker_id`.

        Args:
            all_segments (list[Segment]): The full list of transcript segments.
            target_segment_index (int): The index of the segment to analyze.

        Returns:
            list[Segment]: NOT chronologically ordered list of segments from the same speaker, NOT including the
            target segment, only neighbors.
        """
        # to the left
        total_segments = len(all_segments)
        local_index = target_segment_index
        target_segment_speaker = all_segments[target_segment_index].speaker_id
        result_segments = []

        local_index -= 1
        while local_index >= 0 and all_segments[local_index].speaker_id == target_segment_speaker:
            result_segments.append(all_segments[local_index])
            local_index -= 1

        # to the right
        local_index = target_segment_index
        local_index += 1
        while local_index < total_segments and all_segments[local_index].speaker_id == target_segment_speaker:
            result_segments.append(all_segments[local_index])
            local_index += 1

        return result_segments
