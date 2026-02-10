"""
Does the same as model, but uses LmStudios API / OpenAI's API instead
"""

import logging
import json
import re
import lmstudio as lms
from openai import OpenAI

class Model_API():

    def __init__(
            self,
            config: str | None = None,
            model: str | None = None,
            url: str | None = None,
        ):

        self.config = config
        self.model = model
        self.url = url or 'http://127.0.0.1:1234/v1'
        # Setup OpenAI client
        self.client = OpenAI(
            base_url=self.url,
            api_key="ligegyldigt"
        )

        if self.config is not None:
            if self.model is None:
                self.model = self.config["model"]
        
    
    def response(self, system_prompt = None, prompt = None, text_format = None, raw_output = False, model = None, reasoning = None):
        """
        Docstring for response
        
        :param self: 
        :param system_prompt: System prompt in str (can be None)
        :param prompt: Prompt in str
        :param text_format: If you want strcutured format output
        :param raw_output: Set to true if you want all info from output (response instead of response.output_text)
        :param model: Set model if not in config or in object constructor
        :param reasoning: Set reasoning if you don't want default
        """
        
        # Sæt nuværende model, hvis ingen model
        if model is None:
            model = self.model

        # Build input
        model_input = []

        if system_prompt is not None:
            model_input.append({"role": "system", "content": system_prompt})
        
        if prompt is not None:
            model_input.append({"role": "user", "content": prompt})

        params = {
            "model": model,
            "input": model_input
        }
        
        # Handle text_format and reasoning if available
        if text_format is not None:
            params["text_format"] = text_format
        if reasoning is not None:
            params["reasoning"] = {"effort": reasoning}
        
        # Generate response
        response = self.client.responses.parse(**params)

        # Retuner struktureret format
        if raw_output:
            return response
        elif text_format:
            return response.output_parsed
        else:
            return response.output_text
        
        
        



