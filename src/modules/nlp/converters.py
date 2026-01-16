from conllu import TokenList, parse
import json


class UdpipeJsonToConlluConverter:
    """
    Class for converting UDPipe JSON output (where 'result' is a Conllu formatted string) to the conllu.TokenList
    objects.
    """
    def convert(self, udpipe_json_file_path: str) -> list[TokenList]:
        """
        Reads the JSON file, extracts the raw Conllu string from the 'result' field, and parses it using the
        conllu library.
        Args:
            udpipe_json_file_path (str): Path to the JSON file.
        Returns:
            list[TokenList]: A list of parsed sentences.
        """
        try:
            with open(udpipe_json_file_path, "r", encoding="utf-8") as json_file:
                data = json.load(json_file)

        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error while loading JSON file: {e}")
            return []

        conllu_string = data.get("result", "")
        if not conllu_string:
            print(f"Field 'result in the JSON file {udpipe_json_file_path} is empty!'")
            return []

        sentences = parse(conllu_string)
        return sentences
