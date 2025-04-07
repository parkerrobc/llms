import sys
from typing import Generator, Union

import anthropic

from .ai_abc import AIAbstractClass, AnthropicConfig


class AnthropicService(AIAbstractClass):
    def __init__(self, config: AnthropicConfig, tone: str):
        super().__init__(config, tone)
        self.MESSAGES: [] = []
        if config['key']:
            self.ANTHROPIC = anthropic.Anthropic(api_key=config['key'])
        else:
            self.ANTHROPIC = anthropic.Anthropic()

        return

    def update_messages(self, message: str = '', user_message: str = '', full_history: [] = None):
        if full_history:
            self.MESSAGES = full_history
        if message:
            self.MESSAGES.append({
                    "role": "assistant",
                    "content": message
                })
        if user_message:
            self.MESSAGES.append({
                "role": "user",
                "content": user_message
            })

    def make_assistant_request(self) -> str:
        method_args: dict = {
            'model': self.config['model'],
            'max_tokens': self.config['maxTokens'],
            'temperature': self.config['temperature'],
            'system': self.tone,
            'messages': self.MESSAGES,
        }

        yield from self.__simple_request(method_args)

    def message_builder(self, request: str) -> []:
        user_content = (request or self.config['request']) \
            if self.request_char_limit <= 0 \
            else (request or self.config['request'])[:self.request_char_limit]

        messages = [
            {
                "role": "user",
                "content": user_content
            }
        ]

        return messages

    def __simple_request(self, method_args) -> str:
        response = self.ANTHROPIC.messages.create(**method_args)

        if not response.content:
            print("\nAnthropic Library request failed\n")
            sys.exit(1)

        for content in response.content:
            yield content.text

    def __stream_request(self, method_args) -> str:
        response = self.ANTHROPIC.messages.stream(**method_args)

        if not response:
            print("\nAnthropic Library request failed\n")
            sys.exit(1)

        with response as stream:
            for text in stream.text_stream:
                yield text.replace("\n", " ").replace("\r", " ")

    def make_request(self, tone: str, request: str, json: bool, stream: bool) \
            -> Union[Generator[str, None, None], str]:

        messages = self.message_builder(request)

        method_args: dict = {
            'model': self.config['model'],
            'max_tokens': self.config['maxTokens'],
            'temperature': self.config['temperature'],
            'system': f"{self.tone}. {tone}" if tone else self.tone,
            'messages': messages,
        }

        if stream:
            yield from self.__stream_request(method_args)
        else:
            yield from self.__simple_request(method_args)
