# a function or class that takes "dirty" text, removes punctuation, and returns a list of lemmas via UDPipe
from schemas import EvalSegment
from src.modules.nlp.udpipe_handler import UDPipeHandler
from conllu import parse


class NLPEngine:
    def __init__(self):
        self.udpipe_handler = UDPipeHandler()

    def add_lemmas_to_segments(self, segments: list[EvalSegment]) -> list[EvalSegment]:
        """
        Go through segments and fills .lemmas field. It makes requests to the UDPipe in order to get lemmas.
        Args:
            segments:

        Returns:

        """
        for seg in segments:
            if seg.lemmas:
                continue

            udpipe_response = self.udpipe_handler.process_text(seg.speech)
            connlu_text = udpipe_response.get("result", "")

            if not connlu_text:
                continue
            sentences = parse(connlu_text)

            lemmas = []
            for sentence in sentences:
                for token in sentence:
                    if token.get("upos", "") != "PUNCT":  # ommit punctuation
                        lemma = token.get("lemma")
                        if lemma:
                            lemmas.append(lemma.lower())

            seg.lemmas = lemmas
        return segments
