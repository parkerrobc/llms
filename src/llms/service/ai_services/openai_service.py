import sys
from typing import Generator, Union

from openai import OpenAI

from .ai_abc import AIAbstractClass, OpenAIConfig


class OpenAIService(AIAbstractClass):
    def __init__(self, config: OpenAIConfig, tone: str):
        super().__init__(config, tone)
        self.MESSAGES: [] = []
        self.OPENAI: OpenAI

        if config['baseUrl'] and config['key']:
            self.OPENAI = OpenAI(base_url=config['baseUrl'], api_key=config['key'])
        elif config['baseUrl']:
            self.OPENAI = OpenAI(base_url=config['baseUrl'])
        elif config['key']:
            self.OPENAI = OpenAI(api_key=config['key'])
        else:
            self.OPENAI = OpenAI()

    def call_openai_api(self, method_args: dict, stream: bool) \
            -> Union[Generator[str, None, None], str]:
        if stream:
            method_args.__setitem__('stream', True)

        response = self.OPENAI.chat.completions.create(**method_args)

        if not stream:
            if not response.choices:
                print("\nOpenAI Library request failed\n")
                sys.exit(1)
        else:
            if not response:
                print("\nOpenAI Library request failed\n")
                sys.exit(1)

        if stream:
            for chunk in response:
                for choice in chunk.choices:
                    yield choice.delta.content or ''
        else:
            for choice in response.choices:
                yield choice.message.content or ''

    def update_messages(self, message: str = None, user_message: str = None, full_history: [] = None):
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

    def make_assistant_request(self, stream: bool) -> str:
        messages = [
            {
                "role": "system",
                "content": self.tone
            }
        ]

        messages = messages + self.MESSAGES

        method_args: dict = {
            'model': self.config['model'],
            'messages': messages,
        }

        if self.config['temperature']:
            method_args.__setitem__('temperature', self.config['temperature'])

        yield from self.call_openai_api(method_args, stream)

    def message_builder(self, tone: str = '', request: str = '') -> []:
        system_content = f"{self.tone}. {tone}" if tone else self.tone
        user_content = (request or self.config['request']) \
            if self.request_char_limit <= 0 \
            else (request or self.config['request'])[:self.request_char_limit]

        messages = [
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": user_content
            }
        ]

        return messages

    def make_request(self, tone: str, request: str, json: bool, stream: bool) \
            -> Union[Generator[str, None, None], str]:

        messages = self.message_builder(tone, request)

        method_args: dict = {
            'model': self.config['model'],
            'messages': messages,
        }

        if json:
            method_args.__setitem__('response_format', {"type": "json_object"})
        if self.config['temperature']:
            method_args.__setitem__('temperature', self.config['temperature'])

        yield from self.call_openai_api(method_args, stream)
