# orchestrator

# There is only one main function (compare) that:
# calls Loader.
#
# calls NLP_Engine for both lists.
#
# passes results to Aligner to create pairs.
#
# loops through pairs and calls Metrics.
#
# collects everything into FinalReport
from loaders import ParserFactory
from nlp_engine import NLPEngine
from aligner import TimelineAligner
from metrics import MetricsEvaluator
from schemas import FinalEvaluationReport, ComparisonPair


class ComparisonEngine:
    def __init__(self):
        self.nlp = NLPEngine()
        self.aligner = TimelineAligner()
        self.evaluator = MetricsEvaluator()

    def compare(self, ref_path: str, hyp_path: str) -> FinalEvaluationReport:
        ref_parser = ParserFactory.get_parser(ref_path)
        hyp_parser = ParserFactory.get_parser(hyp_path)

        print("Parsing reference and hypothesis...")
        ref_segments = ref_parser.parse(ref_path)
        hyp_segments = hyp_parser.parse(hyp_path)

        print("Adding lemmas to all segments...")
        ref_segments = self.nlp.add_lemmas_to_segments(ref_segments)
        hyp_segments = self.nlp.add_lemmas_to_segments(hyp_segments)

        # align
        print("Aligning segments...")
        pairs = self.aligner.align(ref_segments, hyp_segments)

        print("Evaluating...")
        for pair in pairs:
            self.evaluator.evaluate(pair)

        # for debugging
        self.perform_error_analysis(pairs)
        return self._build_report(pairs)

    def _build_report(self, pairs: list[ComparisonPair]) -> FinalEvaluationReport:
        if not pairs:
            return FinalEvaluationReport(0.0, 0.0, [], 0)

        total_pairs = len(pairs)
        sum_jaccard = 0.0
        gender_matches = 0

        for pair in pairs:
            sum_jaccard += pair.metrics.get("text_jaccard", 0)
            gender_matches += int(pair.metrics.get("gender", False))

        report = FinalEvaluationReport(
            avg_jaccard=round(sum_jaccard / total_pairs, 4),
            gender_accuracy=round((gender_matches / total_pairs) * 100, 2),
            pairs=pairs,
            total_pairs=total_pairs,
            pairs_data=[{
                "id": i,
                "ref": " ".join([s.speech for s in p.ref_segments]),
                "hyp": " ".join([s.speech for s in p.hyp_segments]),
                "scores": p.metrics
            } for i, p in enumerate(pairs)]
        )

        return report

    def perform_error_analysis(self, pairs: list[ComparisonPair], threshold: float = 0.4):
        print(f"\ERROR ANALYSIS (Jaccard < {threshold})")

        worst_pairs = [p for p in pairs if p.metrics.get("text_jaccard", 1.0) < threshold]

        if not worst_pairs:
            print("No problems found.")
            return

        for i, pair in enumerate(worst_pairs):
            ref_text = " ".join([s.speech for s in pair.ref_segments])
            hyp_text = " ".join([s.speech for s in pair.hyp_segments])

            j_score = pair.metrics.get("jaccard_score", 0.0)

            print(f"\n[Problematic Pair #{i + 1}]")
            print(f"  - REF (reference): {ref_text}")
            print(f"  - HYP (hypothesis):    {hyp_text}")
            print(f"  - Jaccard:      {j_score:.4f}")
            print(f"  - Gender Match: {pair.metrics.get('gender_match')}")
            print("-" * 80)

        print(f"\nTotal problematic pairs found: {len(worst_pairs)}")
