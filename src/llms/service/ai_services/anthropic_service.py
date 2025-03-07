import sys

import anthropic

from .ai_abc import AIAbstractClass, AnthropicConfig


class AnthropicService(AIAbstractClass):
    ANTHROPIC: anthropic.Anthropic

    def __init__(self, config: AnthropicConfig):
        super().__init__(config)
        if config['key']:
            self.ANTHROPIC = anthropic.Anthropic(api_key=config['key'])
        else:
            self.ANTHROPIC = anthropic.Anthropic()

        return

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

    def make_request(self, tone: str, request: str, json: bool, stream: bool) -> str:
        messages = self.message_builder(request)

        method_args: dict = {
            'model': self.config['model'],
            'max_tokens': self.config['maxTokens'],
            'temperature': self.config['temperature'],
            'system': tone or self.config['tone'],
            'messages': messages,
        }

        if stream:
            yield from self.__stream_request(method_args)
        else:
            yield from self.__simple_request(method_args)
