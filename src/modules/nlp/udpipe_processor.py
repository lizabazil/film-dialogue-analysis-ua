import os
import requests
import json


class UdpipeHandler:
    def __init__(self, api_url: str = "http://localhost:3000/process", model_name: str = "ukr"):
        """
        Initializing client.
        """
        self.api_url = api_url
        self.model_name = model_name

    def _send_request(self, data: dict) -> dict:
        """
        Private method to make request.
        """
        url = f"{self.api_url}/process"

        try:
            response = requests.post(url, json=data)
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
            "data": text,
            "model": self.model_name,
            "tokenizer": "",
            "tagger": "",
            "parser": ""
        }
        return self._send_request(data)

    def process_file(self, input_file_path: str, output_file_path: str = None) -> str | None:
        pass

