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
        """
        url = f"{self.api_url}/process"

        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Could not get response from the server: {e}")
            raise Exception()

    def process_text(self, text: str) -> dict:
        """
        Send text to the server udpipe and returns result in a dict format.
        """
        data = {
            "tokenizer": "",
            "tagger": "",
            "parser": "",
            "data": text,
        }
        return self._send_request(data)

    def process_file(self, input_file_path: str, output_file_path: str = None) -> str:
        """
        Reads file with given path, processes its content with UDPipe pipeline, and saves the result to the output file
        optionally.
        """
        with open(input_file_path, 'r') as file:
            content = file.read()

        udpipe_result = self.process_text(content)
        if output_file_path:   # save to the file
            with open(output_file_path, "w") as file:
                json.dump(udpipe_result, file, indent=4, ensure_ascii=False)

        return str(udpipe_result)

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
