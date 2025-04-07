import sys
from typing import Generator, Union

from openai import OpenAI

from .ai_abc import AIAbstractClass, OpenAIConfig


class OpenAIService(AIAbstractClass):
    OPENAI: OpenAI

    def __init__(self, config: OpenAIConfig, tone: str):
        super().__init__(config, tone)
        if config['baseUrl'] and config['key']:
            self.OPENAI = OpenAI(base_url=config['baseUrl'], api_key=config['key'])
        elif config['baseUrl']:
            self.OPENAI = OpenAI(base_url=config['baseUrl'])
        elif config['key']:
            self.OPENAI = OpenAI(api_key=config['key'])
        else:
            self.OPENAI = OpenAI()

    def make_history_request(self, my_messages: [str], other_messages: [[str]], first: bool = False) -> str:
        history_messages = [
            {
                "role": "system",
                "content": self.tone
            }
        ]

        if first:
            for message in zip(*[my_messages, *other_messages]):
                history_messages.append({
                    "role": "assistant",
                    "content": message[0]
                })
                for number in [i + 1 for i in range(len(message) - 1)]:
                    history_messages.append({
                        "role": "user",
                        "content": message[number]
                    })
        else:
            for message in zip(*[my_messages, *other_messages]):
                for number in [i + 1 for i in range(len(message) - 1)]:
                    history_messages.append({
                        "role": "user",
                        "content": message[number]
                    })
                history_messages.append({
                    "role": "assistant",
                    "content": message[0]
                })
            for other_message in other_messages:
                if len(my_messages) < len(other_message):
                    history_messages.append({
                        "role": "user",
                        "content": other_message[-1]
                    })

        method_args: dict = {
            'model': self.config['model'],
            'messages': history_messages,
        }

        if self.config['temperature']:
            method_args.__setitem__('temperature', self.config['temperature'])

        response = self.OPENAI.chat.completions.create(**method_args)

        if not response.choices:
            print("\nOpenAI Library request failed\n")
            sys.exit(1)

        for choice in response.choices:
            yield choice.message.content or ''

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
        if stream:
            method_args.__setitem__('stream', True)
        if self.config['temperature']:
            method_args.__setitem__('temperature', self.config['temperature'])

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
