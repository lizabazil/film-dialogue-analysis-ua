# this file will be using all methods for identifying the gender of the speaker
from audio_gender_extractor import AudioGenderExtractor
from visual_gender_extractor import VisualGenderExtractor
from text_gender_extractor import TextGenderExtractor
from src.utils.segment import Segment


class GenderEnricher:
    """
    Main class which uses different approaches to detect the gender of the speaker.
    """
    # TODO: implement
    def __init__(self, config: dict = None):
        self.weights = {
            "audio": config.get("speaker_enrichment", {}).get("voting_weights", {}).get("audio", {}),
            "image": config.get("speaker_enrichment", {}).get("voting_weights", {}).get("image", {}),
            "text": config.get("speaker_enrichment", {}).get("voting_weights", {}).get("text", {})
        }
        self.audio_gender_extractor = AudioGenderExtractor(config)
        self.visual_gender_extractor = VisualGenderExtractor(config)
        self.text_gender_extractor = TextGenderExtractor()

    def annotate_segments(self, video_path: str, all_segments: list[Segment]):
        """
        Segments may not be already joined by the same speaker (especially if the pause is significant).
        Args:
            video_path:
            all_segments:

        Returns:

        """
        audio_result = self.audio_gender_extractor.predict_gender(video_path, ...)
        visual_result = self.visual_gender_extractor.predict_gender(video_path, ...)
        text_result = self.text_gender_extractor.predict_gender(..., ...)
        # TODO: implement
        pass

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
