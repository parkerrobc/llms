import sys

from openai import OpenAI

from .ai_protocol import AIProtocol


class OpenAIService(AIProtocol):
    OPENAI: OpenAI

    def initialize(self) -> None:
        config = self.CONFIG

        if config['baseUrl'] and config['key']:
            self.OPENAI = OpenAI(base_url=config['baseUrl'], api_key=config['key'])
        elif config['baseUrl']:
            self.OPENAI = OpenAI(base_url=config['baseUrl'])
        elif config['key']:
            self.OPENAI = OpenAI(api_key=config['key'])
        else:
            self.OPENAI = OpenAI()

    def message_builder(self, tone: str, request: str) -> []:
        messages = [{
            "role": "system",
            "content": tone or self.DEFAULT_TONE
        },
            {
                "role": "user",
                "content": (request or self.DEFAULT_REQUEST)[:self.REQUEST_CHAR_LIMIT]
            }
        ]

        return messages

    def make_request(self, tone: str, request: str, json: bool, stream: bool) -> str:
        messages = self.message_builder(tone, request)

        method_args: dict = {
            'model': self.MODEL,
            'messages': messages,
        }

        if json:
            method_args.__setitem__('response_format', {"type": "json_object"})
        if stream:
            method_args.__setitem__('stream', True)

        response = self.OPENAI.chat.completions.create(**method_args)

        if not response.choices:
            print("\nOpenAI Library request failed\n")
            sys.exit(1)

        if stream:
            for chunk in response:
                for choice in chunk.choices:
                    yield choice.delta.content or ''
        else:
            for choice in response.choices:
                yield choice.message.content or ''


