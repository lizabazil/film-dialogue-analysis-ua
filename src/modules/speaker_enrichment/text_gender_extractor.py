# TODO: implement
from src.utils.segment import Segment
from conllu.models import Token, TokenList


class TextGenderExtractor:
    def __init__(self):
        pass

    def predict_gender(self, target_segment: Segment, neighboring_segments: list[Segment]) -> dict | None:
        if target_segment.nlp_data:  # if we have udpipe parsed data
            for sentence in target_segment.nlp_data:
                for token in sentence:
                    pos = token["upos"]   # part of speech
                    feats = token["feats"]
                    head_id = token["head"]
                    id = token["id"]


        return None

    @staticmethod
    def _get_head_by_id(sentence: TokenList, head: int) -> Token | None:
        for token in sentence:
            if token["id"] == head:
                return token
        return None

    @staticmethod
    def _is_past_time(token: Token) -> bool:
        """
        Checks if the token is a verb in the past tense.

        Args:
            token (Token): Given token with linguistic features (parsed by conllu).
        Returns:
            bool: True if it is a past tense verb, False otherwise.
        """
        feats = token.get("feats")
        return feats and feats.get("Tense", "") == 'Past'

    @staticmethod
    def _is_present_time(token: Token) -> bool:
        """
        Checks if the token is a verb in the present tense.

        Args:
            token (Token): Given token with linguistic features (parsed by conllu).
        Returns:
            bool: True if it is a present tense verb, False otherwise.
        """

        feats = token.get("feats")
        return feats and feats.get("Tense", "") == 'Pres'

    @staticmethod
    def _is_verb(token: Token) -> bool:
        """
        Check if the token is a verb.

        Args:
            token (Token): Given token with linguistic features (parsed by conllu).
        Returns:
            bool: True if it is a verb, False otherwise.
        """
        return token.get("upos") == "VERB"

    @staticmethod
    def _is_first_person(token: Token) -> bool:
        """
        Checks if the token refers to the first person (e.g., "я", "ми").
        This method inspects the 'Person' key in the token's morphological
        features dictionary to see if it equals '1'.

        Args:
            token (Token): Given token with linguistic features (parsed by conllu).

        Returns:
            bool: True if the token indicates 1st person (Person='1'), False otherwise.
        """
        feats = token.get("feats")
        return feats and feats.get("Person", "") == "1"

    @staticmethod
    def _is_second_person(token: Token) -> bool:
        """
        Checks if the token refers to the second person (e.g., "ти", "ви").
        This method inspects the 'Person' key in the token's morphological
        features dictionary to see if it equals '2'.

        Args:
            token (Token): Given token with linguistic features (parsed by conllu).

        Returns:
            bool: True if the token indicates 2nd person (Person='2'), False otherwise.
        """

        feats = token.get("feats")
        return feats and feats.get("Person", "") == "2"

    @staticmethod
    def _is_third_person(token: Token) -> bool:
        """
        Checks if the token refers to the third person (e.g., "він", "вони").
        This method inspects the 'Person' key in the token's morphological
        features dictionary to see if it equals '3'.

        Args:
            token (Token): Given token with linguistic features (parsed by conllu).

        Returns:
            bool: True if the token indicates 3rd person (Person='3'), False otherwise.
        """

        feats = token.get("feats")
        return feats and feats.get("Person", "") == "3"

    @staticmethod
    def _is_male(token: Token) -> bool:
        """
        Checks if the token has the masculine grammatical gender feature.
        This method inspects the 'Gender' key in the token's morphological features dictionary to see if it equals
        'Masc'.

        Args:
            token (Token): Given token with linguistic features (parsed by conllu).

        Returns:
            bool: True if the token indicates masculine gender (Gender='Masc'), False otherwise.
        """
        feats = token.get("feats")
        return feats and feats.get("Gender", "") == "Masc"

    @staticmethod
    def _is_female(token: Token) -> bool:
        """
        Checks if the token has the female grammatical gender feature.
        This method inspects the 'Gender' key in the token's morphological features dictionary to see if it equals
        'Fem'.

        Args:
            token (Token): Given token with linguistic features (parsed by conllu).

        Returns:
            bool: True if the token indicates female gender (Gender='Fem'), False otherwise.
        """

        feats = token.get("feats")
        return feats and feats.get("Gender", "") == "Fem"
