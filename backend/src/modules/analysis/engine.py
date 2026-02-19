from schemas import MovieAnalysisReport


class AnalysisEngine:
    def __int__(self, jsonl_path: str):
        self.jsonl_paht = jsonl_path
        self.segments = self._load_data()

    def _load_data(self):
        # load data from jsonl to the segments
        pass

    def run_full_analysis(self) -> MovieAnalysisReport:
        pass
