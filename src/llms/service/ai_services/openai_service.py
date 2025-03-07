import sys

from openai import OpenAI

from .ai_abc import AIAbstractClass, OpenAIConfig


class OpenAIService(AIAbstractClass):
    OPENAI: OpenAI

    def __init__(self, config: OpenAIConfig):
        super().__init__(config)
        if config['baseUrl'] and config['key']:
            self.OPENAI = OpenAI(base_url=config['baseUrl'], api_key=config['key'])
        elif config['baseUrl']:
            self.OPENAI = OpenAI(base_url=config['baseUrl'])
        elif config['key']:
            self.OPENAI = OpenAI(api_key=config['key'])
        else:
            self.OPENAI = OpenAI()

    def message_builder(self, tone: str, request: str) -> []:
        system_content = tone or self.config['tone']
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

    def make_request(self, tone: str, request: str, json: bool, stream: bool) -> str:
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
