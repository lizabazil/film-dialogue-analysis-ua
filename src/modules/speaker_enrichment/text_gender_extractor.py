# TODO: implement
from src.utils.segment import Segment
from conllu.models import Token, TokenList
from src.modules.speaker_enrichment.constants import TokenKeys, Upos, FeatKeys, FeatValues, Deprel


class TextGenderExtractor:
    CONFIDENCE_DICT = {"adj": 0.8, "noun": 0.3}

    def __init__(self):
        pass

    def predict_gender(self, target_segment: Segment, neighboring_segments: list[Segment]) -> dict | None:
        if target_segment.nlp_data:  # if we have udpipe parsed data
            for sentence in target_segment.nlp_data:
                # for testing
                print(f"detected by the _second_person_sing_past_time: "
                      f"{TextGenderExtractor._second_person_sing_past_tense(sentence)}")
        return None

    @staticmethod
    def _second_person_sing_past_tense(sentence: TokenList) -> str | None:
        """
        Determines the gender of the addressee based on a 2nd person singular subject and a past tense verb.

        This method searches for a nominal subject ('nsubj') representing the 2nd person singular (e.g., "ти").
        If found, it inspects the head word. If the head is a verb in the past tense, the method returns its
        grammatical gender.

        Args:
            sentence (TokenList): The parsed sentence containing tokens with linguistic features.

        Returns:
            str | None: 'male' or 'female' if a gendered past tense verb linked to the 2nd person subject is found;
            otherwise None.
        """
        for token in sentence:
            if (TextGenderExtractor._is_pronoun(token) and TextGenderExtractor._is_number_sing(token) and
                    TextGenderExtractor._is_second_person(token) and TextGenderExtractor._is_nominal_subject(token)):
                # go to the head
                head_id = TextGenderExtractor._get_head_id(token)
                head_token = TextGenderExtractor._get_token_by_id_in_the_sentence(sentence, head_id)

                if not head_token:
                    continue
                # look for the verb in past tense
                if TextGenderExtractor._is_verb(head_token) and TextGenderExtractor._is_past_tense(head_token):
                    if TextGenderExtractor._is_male(head_token):
                        return 'male'
                    if TextGenderExtractor._is_female(head_token):
                        return 'female'
        return None

    @staticmethod
    def _first_person_sing_past_tense(sentence: TokenList) -> str | None:
        """
        Determines the gender of the speaker based on a 1st person singular subject and a past tense verb.

        This method searches for a nominal subject ('nsubj') representing the 1st person singular (e.g., "я").
        If found, it inspects the head word. If the head is a verb in the past tense, the method returns its
        grammatical gender.

        Args:
            sentence (TokenList): The parsed sentence containing tokens with linguistic features.

        Returns:
            str | None: 'male' or 'female' if a gendered past tense verb linked to the  1st person subject is found;
            otherwise None.
        """
        for token in sentence:
            if (TextGenderExtractor._is_pronoun(token) and TextGenderExtractor._is_first_person(token) and
                    TextGenderExtractor._is_nominal_subject(token) and TextGenderExtractor._is_number_sing(token)):
                # go to the head
                head_id = TextGenderExtractor._get_head_id(token)
                head_token = TextGenderExtractor._get_token_by_id_in_the_sentence(sentence, head_id)
                if not head_token:
                    continue

                # check for verb in past tense
                if TextGenderExtractor._is_verb(head_token) and TextGenderExtractor._is_past_tense(token):
                    if TextGenderExtractor._is_female(head_token):
                        return "female"
                    if TextGenderExtractor._is_male(head_token):
                        return "male"
        return None

    @staticmethod
    def _infer_gender_from_noun_or_adj_head(sentence: TokenList) -> tuple[str, float] | None:
        """
        Infers gender from 1st or 2nd person subjects (both siglular and plural) linked to a Noun or Adjective head.

        This method handles cases like "Я гарний" (Adjective) or "Я лікар" (Noun).
        It searches for a pronoun subject ('nsubj') and inspects the gender of its syntactic head.

        WARNING:
            This method is heuristic and has varying reliability:
            - Adjectives (Singular): High reliability (e.g., "Я втомлена" -> Fem).
            - Nouns: Low reliability due to fixed grammatical gender (e.g., "Я людина" is grammatically Fem, but can
            be said by a male; "Ми лікарі" is Masc, but can refer to women as well).

        Args:
            sentence (TokenList): The parsed sentence containing tokens with linguistic features.

        Returns:
            tuple[str, float] | None: A tuple containing:
                - The gender ('male' or 'female') or None if not found.
                - A confidence score (e.g.,higher for Adjectives and lower for Nouns). Otherwise, None is returned.
        """
        for token in sentence:
            if TextGenderExtractor._is_pronoun(token) and TextGenderExtractor._is_nominal_subject(token):
                head_id = TextGenderExtractor._get_head_id(token)  # find the head
                head_token = TextGenderExtractor._get_token_by_id_in_the_sentence(sentence, head_id)

                is_head_noun = TextGenderExtractor._is_noun(head_token)
                is_head_adjective = TextGenderExtractor._is_adjective(head_token)
                is_head_female = TextGenderExtractor._is_female(head_token)
                is_head_male = TextGenderExtractor._is_male(head_token)

                result_gender = None
                if is_head_female:
                    result_gender = "female"
                elif is_head_male:
                    result_gender = "male"
                # set confidence score looking whether it was adjective or noun
                confidence_score = ((is_head_noun and TextGenderExtractor.CONFIDENCE_DICT.get("noun")) or
                                    (is_head_adjective and TextGenderExtractor.CONFIDENCE_DICT.get("adj")) or None)

                if result_gender and confidence_score:
                    return result_gender, confidence_score
        return None  # no gender was found

    @staticmethod
    def _get_token_by_id_in_the_sentence(sentence: TokenList, token_id: int) -> Token | None:
        """
        Retrieves a token from the sentence based on its CoNLL-U ID.

        Args:
            sentence (TokenList): The parsed sentence containing the tokens.
            token_id (int): The linguistic ID of the token to search for.
        Returns:
            Token | None: The matching Token object if found, otherwise None.
        """
        for token in sentence:
            if token.get(TokenKeys.ID) == token_id:
                return token
        return None

    @staticmethod
    def _is_past_tense(token: Token) -> bool:
        """
        Checks if the token is a verb in the past tense.

        Args:
            token (Token): Given token with linguistic features (parsed by conllu).
        Returns:
            bool: True if it is a past tense verb, False otherwise.
        """
        feats = token.get(TokenKeys.FEATS)
        return feats and feats.get(FeatKeys.TENSE, "") == FeatValues.PAST

    @staticmethod
    def _is_present_tense(token: Token) -> bool:
        """
        Checks if the token is a verb in the present tense.

        Args:
            token (Token): Given token with linguistic features (parsed by conllu).
        Returns:
            bool: True if it is a present tense verb, False otherwise.
        """

        feats = token.get(TokenKeys.FEATS)
        return feats and feats.get(FeatKeys.TENSE, "") == FeatValues.PRES

    @staticmethod
    def _is_verb(token: Token) -> bool:
        """
        Check if the token is a verb.

        Args:
            token (Token): Given token with linguistic features (parsed by conllu).
        Returns:
            bool: True if it is a verb, False otherwise.
        """
        return token.get(TokenKeys.UPOS, "") == Upos.VERB

    @staticmethod
    def _is_adjective(token: Token) -> bool:
        """
        Check if the token is an adjective.

        Args:
            token (Token): Given token with linguistic features (parsed by conllu).
        Returns:
            bool: True if it is an adjective, False otherwise.
        """
        return token.get(TokenKeys.UPOS, "") == Upos.ADJ

    @staticmethod
    def _is_noun(token: Token) -> bool:
        """
        Check if the token is a noun.

        Args:
            token (Token): Given token with linguistic features (parsed by conllu).
        Returns:
            bool: True if it is a noun, False otherwise.
        """
        return token.get(TokenKeys.UPOS, "") == Upos.NOUN

    @staticmethod
    def _is_pronoun(token: Token) -> bool:
        """
        Check if the token is a pronoun.
        Args:
            token (Token): Given token with linguistic features (parsed by conllu).
        Returns:
            bool: True if it is a pronoun, False otherwise.
        """
        return token.get(TokenKeys.UPOS, "") == Upos.PRON

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
        feats = token.get(TokenKeys.FEATS)
        return feats and feats.get(FeatKeys.PERSON, "") == FeatValues.FIRST

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
        feats = token.get(TokenKeys.FEATS)
        return feats and feats.get(FeatKeys.PERSON, "") == FeatValues.SECOND

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
        feats = token.get(TokenKeys.FEATS)
        return feats and feats.get(FeatKeys.PERSON, "") == FeatValues.THIRD

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
        feats = token.get(TokenKeys.FEATS)
        return feats and feats.get(FeatKeys.GENDER, "") == FeatValues.MASC

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
        feats = token.get(TokenKeys.FEATS)
        return feats and feats.get(FeatKeys.GENDER, "") == FeatValues.FEM

    @staticmethod
    def _is_nominal_subject(token: Token) -> bool:
        """
        Checks if the token plays the role of a nominal subject in the sentence.
        This method inspects the dependency relation ('deprel') of the token to see if it equals 'nsubj'.

        Args:
            token (Token): Given token with linguistic features (parsed by conllu).
        Returns:
            bool: True if the token is a nominal subject ('nsubj'), False otherwise.
        """
        return token.get(TokenKeys.DEPREL, "") == Deprel.NSUBJ

    @staticmethod
    def _is_number_sing(token: Token) -> bool:
        """
        Checks if the token has the singular grammatical number feature.
        This method inspects the 'Number' key in the token's morphological features dictionary to see if it equals
        'Sing'.

        Args:
            token (Token): Given token with linguistic features (parsed by conllu).

        Returns:
            bool: True if the token is in singular form (Number='Sing'), False otherwise.
        """
        feats = token.get(TokenKeys.FEATS)
        return feats and feats.get(FeatKeys.NUMBER, "") == FeatValues.SING

    @staticmethod
    def _get_head_id(token: Token) -> int:
        """
        Retrieves the ID of the token's syntactic head (parent) in the dependency tree.
        This method accesses the 'head' field of the token, which points to the token that governs the current
        token (e.g., the verb governing a subject).

        Args:
            token (Token): Given token with linguistic features (parsed by conllu).

        Returns:
            int: The ID of the head token. A value of 0 typically indicates  that the token is the root of the sentence.
                """
        return token.get(TokenKeys.HEAD)
