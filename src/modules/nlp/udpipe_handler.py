import requests
import json


class UDPipeHandler:
    """
    Class made for handling getting results with UDPipe pipeline.
    """
    def __init__(self, api_url: str = "http://localhost:3000"):
        """
        Initializing client.
        """
        self.api_url = api_url
        if not self._check_connection():
            raise ConnectionError(f"Cannot connect to UDPipe server.")

    def _send_request(self, data: dict) -> dict:
        """
        Private method to make request.
        Args:
            data (dict): Data with info such as tokenizer, parser etc. which are needed for proper request.
        Returns:
            dict: Result from the UDPipe in the dict structure.
        """
        url = f"{self.api_url}/process"

        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Could not get response from the server: {e}")
            raise Exception()

    def process_text(self, text: str, output_json_file_path: str = None) -> dict:
        """
        Send text to the server udpipe and returns result in a dict format.
        Args:
            text (str): Input text.
            output_json_file_path (str): An optional argument for writing the result to the JSON file. If None is given,
            the result is not being written to the file.
        Returns:
            dict: Result from the UDPipe in the dict structure.
        """
        data = {
            "tokenizer": "presegmented",
            "tagger": "",
            "parser": "",
            "data": text,
        }
        res = self._send_request(data)
        if output_json_file_path:
            with open(output_json_file_path, "w") as f:
                json.dump(res, f, indent=4, ensure_ascii=False)
        return res

    def process_file(self, input_file_path: str, output_file_path: str = None) -> dict:
        """
        Reads file with given path, processes its content with UDPipe pipeline, and saves the result to the output file
        optionally.
        Args:
            input_file_path (str): Path to the input text file.
            output_file_path (str): Path to the JSON output file. In None is passes, then it is not written to the
            file.
        Returns:
            dict: Result from the UDPipe in the dict structure.
        """
        with open(input_file_path, 'r') as file:
            content = file.read()

        udpipe_result = self.process_text(content)
        if output_file_path:   # save to the file
            with open(output_file_path, "w") as file:
                json.dump(udpipe_result, file, indent=4, ensure_ascii=False)

        return udpipe_result

    def _check_connection(self) -> bool:
        """
        Send a simple request to check the connection. It sends short test input to the UDPipe server, which additionally
        allows importing all the necessary libraries during the very first request to the server.

        Returns:
            bool: True if connection is active, False otherwise.
        """
        test_input = "Привіт, світе!"
        test_data = {
            "tokenizer": "",
            "tagger": "",
            "parser": "",
            "data": test_input,

        }
        try:
            response = requests.post(f"{self.api_url}/process", data=test_data)
            response.raise_for_status()
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Connection failed: {e}")
            return False
