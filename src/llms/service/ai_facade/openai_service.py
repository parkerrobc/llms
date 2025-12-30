import sys
from typing import Generator

from openai import OpenAI, Stream, BadRequestError
from openai.types.chat import ChatCompletionMessageToolCall, ChatCompletionChunk, ChatCompletion, ChatCompletionMessage

from .ai_abc import AIAbstractClass, OpenAIConfig

from helpers import inject


@inject(tool_box='tool_box')
class OpenAIService(AIAbstractClass):
    def __init__(self, config: OpenAIConfig):
        super().__init__(config)
        self.MESSAGES: list[dict | ChatCompletionMessage] = []
        self.OPENAI: OpenAI
        self.ignore_tools = False

        if config['baseUrl'] and config['key']:
            self.OPENAI = OpenAI(base_url=config['baseUrl'], api_key=config['key'])
        elif config['baseUrl']:
            self.OPENAI = OpenAI(base_url=config['baseUrl'])
        elif config['key']:
            self.OPENAI = OpenAI(api_key=config['key'])
        else:
            self.OPENAI = OpenAI()

        self.instantiate_messages(use_system_message=True)

    def __handle_tool_call(self, tool_call: ChatCompletionMessageToolCall) \
            -> dict[str, str | dict[str, str]]:
        if isinstance(tool_call, dict):
            tool_call_id = tool_call['id']
            name = tool_call['function']['name']
            arguments = tool_call['function']['arguments']
        else:
            tool_call_id = tool_call.id
            name = tool_call.function.name or tool_call['function']['name']
            arguments = tool_call.function.arguments or tool_call['function']['arguments']

        tool_result = self.tool_box.handle_tool_call(name, arguments)

        return {
            "tool_call_id": tool_call_id,
            "role": "tool",
            "name": name,
            "content": tool_result
        }

    def __handle_stream_response(self, response: Stream[ChatCompletionChunk]) \
            -> Generator[str]:
        if not response:
            print("\nOpenAI Library request failed\n")
            sys.exit(1)

        for chunk in response:
            if not chunk or not chunk.choices:
                continue
            for choice in chunk.choices:
                calls = []
                if choice.delta.tool_calls:
                    for tool_call in choice.delta.tool_calls:
                        if len(calls) <= tool_call.index:
                            calls.append(
                                {
                                    "id": "",
                                    "type": "function",
                                    "function": {
                                        "name": "",
                                        "arguments": ""
                                    }
                                })

                        call = calls[tool_call.index]

                        if tool_call.id:
                            call["id"] += tool_call.id
                        if tool_call.function.name:
                            call["function"]["name"] += tool_call.function.name
                        if tool_call.function.arguments:
                            call["function"]["arguments"] += tool_call.function.arguments

                    if calls:
                        for call in calls:
                            tool_result = self.__handle_tool_call(call)
                            self.update_messages(single_message=tool_result)

                    yield from self.make_assistant_request(False, True, False)
                else:
                    yield choice.delta.content

    def __handle_response(self, response: ChatCompletion) \
            -> Generator[str]:
        if not response.choices:
            print("\nOpenAI Library request failed\n")
            sys.exit(1)

        for choice in response.choices:
            message = choice.message

            if message.tool_calls and choice.finish_reason == "tool_calls":
                for tool_call in message.tool_calls:
                    tool_result = self.__handle_tool_call(tool_call)

                    self.update_messages(single_message=message)
                    self.update_messages(single_message=tool_result)

                yield from self.make_assistant_request(False, False, False)
            else:
                yield choice.message.content or ''

    def call_openai_api(self, json: bool, stream: bool, use_tools: bool) \
            -> Generator[str]:

        method_args: dict = {
            'model': self.config['model'],
            'messages': self.MESSAGES,
        }

        if json:
            method_args.__setitem__('response_format', {"type": "json_object"})
        if stream:
            method_args.__setitem__('stream', True)
        if use_tools and not self.ignore_tools:
            method_args.__setitem__('tools', self.tool_box.get_tools())
            method_args.__setitem__('tool_choice', 'auto')
        if self.config['temperature']:
            method_args.__setitem__('temperature', self.config['temperature'])

        try:
            response = self.OPENAI.chat.completions.create(**method_args)
        except BadRequestError as e:
            self.ignore_tools = True
            print(f'exception: {e}')
            method_args.__delitem__('tools')
            method_args.__delitem__('tool_choice')
            response = self.OPENAI.chat.completions.create(**method_args)

        if stream:
            yield from self.__handle_stream_response(response)
        else:
            yield from self.__handle_response(response)

    def instantiate_messages(self, system_message: str = None, use_system_message: bool = False):
        if use_system_message:
            self.MESSAGES = [{
                "role": "system",
                "content": f"{self.tone}. {system_message}" if system_message else self.tone
            }]
            if self.config['request']:
                self.MESSAGES.append({
                    "role": "user",
                    "content": f'{self.config['request']}'
                })
        else:
            self.MESSAGES = []

    def update_messages(self, use_system_message: bool = False, system_message: str = None,
                        assistant_message: str = None, user_message: str = None, full_history: list[dict] = None,
                        assistant_thread: bool = False, single_message: dict | ChatCompletionMessage = None):
        if assistant_thread:
            return

        if full_history:
            self.instantiate_messages(system_message, use_system_message)
            self.MESSAGES += full_history
        elif use_system_message:
            self.instantiate_messages(system_message, use_system_message)

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

        if single_message:
            self.MESSAGES.append(single_message)

    def make_assistant_request(self, json: bool, stream: bool, use_tools: bool) -> Generator[str]:
        yield from self.call_openai_api(json, stream, use_tools)

    def make_request(self, tone: str, request: str, json: bool, stream: bool, use_tools: bool) \
            -> Generator[str]:
        self.update_messages(use_system_message=True, system_message=tone, user_message=request, full_history=None)
        yield from self.call_openai_api(json, stream, use_tools)
