from json import dumps
import sys
from typing import Generator, Union

from openai import OpenAI

from .ai_abc import AIAbstractClass, OpenAIConfig

from helpers import inject


@inject(tool_box='tool_box')
class OpenAIService(AIAbstractClass):
    def __init__(self, config: OpenAIConfig):
        super().__init__(config)
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

    def call_openai_api(self, method_args: dict, stream: bool, use_tools: bool) \
            -> Union[Generator[str, None, None], str]:
        if stream:
            method_args.__setitem__('stream', True)
        if use_tools:
            method_args.__setitem__('tools', self.tool_box.tools)
            method_args.__setitem__('tool_choice', 'auto')

        response = self.OPENAI.chat.completions.create(**method_args)

        messages = method_args['messages']

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
                if not chunk:
                    continue
                for choice in chunk.choices:
                    yield choice.delta.content or ''
        else:
            for choice in response.choices:
                message = choice.message

                if message.tool_calls:
                    for tool_call in message.tool_calls:
                        tool_call_id = tool_call.id
                        name = tool_call.function.name
                        arguments = tool_call.function.arguments

                        tool_result = self.tool_box.handle_tool_call(tool_call_id, name, arguments)

                        messages.append(message.model_dump())
                        messages.append(tool_result)

                        yield tool_result['content']

                    tool_response = self.OPENAI.chat.completions.create(model=method_args['model'], messages=messages)

                    for tool_choice in tool_response.choices:
                        yield tool_choice.message.content or ''
                else:
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

    def make_assistant_request(self, stream: bool, use_tools: bool) -> str:
        messages = [
            {
                "role": "developer",
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

        yield from self.call_openai_api(method_args, stream, use_tools)

    def message_builder(self, tone: str = '', request: str = '') -> []:
        developer_content = f"{self.tone}. {tone}" if tone else self.tone
        user_content = (request or self.config['request']) \
            if self.request_char_limit <= 0 \
            else (request or self.config['request'])[:self.request_char_limit]

        messages = [
            {
                "role": "developer",
                "content": developer_content
            },
            {
                "role": "user",
                "content": user_content
            }
        ]

        return messages

    def make_request(self, tone: str, request: str, json: bool, stream: bool, use_tools: bool) \
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

        yield from self.call_openai_api(method_args, stream, use_tools)
