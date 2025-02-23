import os
import sys

from openai import OpenAI, Stream
from dotenv import load_dotenv
from openai.types.chat import ChatCompletionChunk, ChatCompletion

from helpers import Config


def check_key(custom: bool, config: dict) -> str:
    api_key: str

    if custom:
        api_key = config['key']
    else:
        load_dotenv(override=True)
        api_key = config['key'] or os.getenv('OPENAI_API_KEY')

    if api_key and custom:
        return api_key
    elif not custom and api_key.startswith('sk-proj-') and len(api_key) > 10:
        return api_key
    else:
        print("\nInvalid API key\n")
        sys.exit(1)


def check_base_url(custom: bool, config: dict) -> str:
    base_url: str

    if custom:
        base_url = config['baseUrl']
    else:
        return ''

    if base_url:
        return base_url
    else:
        print("\nInvalid base URL\n")
        sys.exit(1)


def __init__openai__lib__(custom: bool, config: dict) -> OpenAI:
    api_key = check_key(custom, config)
    base_url = check_base_url(custom, config)
    return OpenAI(base_url=base_url, api_key=api_key) if custom else OpenAI(api_key=api_key)


class OpenAIService:
    OPENAI: OpenAI

    DEFAULT_TONE: str
    DEFAULT_REQUEST: str

    MODEL: str

    def __init__(self, args, config: Config):
        self.DEFAULT_TONE = config.dict['DEFAULTS']['tone']
        self.DEFAULT_REQUEST = config.dict['DEFAULTS']['request']

        ai_config: dict

        if args.custom:
            ai_config = config.dict['CUSTOM_AI']
        else:
            ai_config = config.dict['OPEN_AI']

        self.OPENAI = __init__openai__lib__(args.custom, ai_config)

        self.MODEL = args.model

    def message_builder(self, tone: str, request: str) -> []:
        messages = []

        if tone:
            messages.append({
                "role": "system",
                "content": tone or self.DEFAULT_TONE
            })

        if request:
            messages.append({
                "role": "user",
                "content": request or self.DEFAULT_REQUEST
            })

        return messages

    def make_request(self, tone: str, request: str, json: bool = False, stream: bool = False) -> Stream[
                                                                                                     ChatCompletionChunk] | ChatCompletion:
        messages = self.message_builder(tone, request)

        method_args: dict = {
            'model': self.MODEL,
            'messages': messages,
        }

        if json:
            method_args.__setitem__('response_format', {"type": "json_object"})
        if stream:
            method_args.__setitem__('stream', True)

        return self.OPENAI.chat.completions.create(**method_args)
