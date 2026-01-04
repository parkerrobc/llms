import sys
from typing import Generator

import anthropic

from .ai_service import AIService, AnthropicConfig


class AnthropicService(AIService):
    def __init__(self, config: AnthropicConfig):
        super().__init__(config)
        self.MESSAGES: list[dict] = []
        if config['key']:
            self.ANTHROPIC = anthropic.Anthropic(api_key=config['key'])
        else:
            self.ANTHROPIC = anthropic.Anthropic()

        return

    def update_messages(self, use_system_message: bool = True, system_message: str = '', assistant_message: str = '',
                        user_message: str = '', full_history: list[dict] | None = None, assistant_thread: bool = False,) -> None:

        for history in (full_history or []):
            if 'metadata' in history:
                del history['metadata']
            if 'options' in history:
                del history['options']

        if full_history:
            self.MESSAGES = full_history
        if assistant_message:
            self.MESSAGES.append({
                    "role": "assistant",
                    "content": assistant_message
                })
        if user_message:
            self.MESSAGES.append({
                "role": "user",
                "content": user_message
            })

    def make_assistant_request(self, json: bool = False, stream: bool = False, use_tools: bool = False) -> Generator[str]:
        method_args: dict = {
            'model': self.config['model'],
            'max_tokens': self.config['maxTokens'],
            'temperature': self.config['temperature'],
            'system': self.tone,
            'messages': self.MESSAGES
        }

        if stream:
            yield from self.__stream_request(method_args)
        else:
            yield from self.__simple_request(method_args)

    def message_builder(self, request: str) -> list[dict]:
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

    def __simple_request(self, method_args) -> Generator[str]:
        response = self.ANTHROPIC.messages.create(**method_args)

        if not response.content:
            print("\nAnthropic Library request failed\n")
            sys.exit(1)

        for content in response.content:
            yield content.text

    def __stream_request(self, method_args) -> Generator[str]:
        response = self.ANTHROPIC.messages.stream(**method_args)

        if not response:
            print("\nAnthropic Library request failed\n")
            sys.exit(1)

        with response as stream:
            for text in stream.text_stream:
                yield text.replace("\n", " ").replace("\r", " ")

    def make_request(self, system_message: str = '', request: str = '', json: bool = False, stream: bool = False, use_tools: bool = False) \
            -> Generator[str]:

        messages = self.message_builder(request)

        method_args: dict = {
            'model': self.config['model'],
            'max_tokens': self.config['maxTokens'],
            'temperature': self.config['temperature'],
            'system': f"{self.tone}. {system_message}" if system_message else self.tone,
            'messages': messages,
        }

        if stream:
            yield from self.__stream_request(method_args)
        else:
            yield from self.__simple_request(method_args)
