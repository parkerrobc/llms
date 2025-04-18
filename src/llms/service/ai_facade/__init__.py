from typing import Generator, Union

from .openai_service import OpenAIService
from .anthropic_service import AnthropicService
from .google_service import GoogleService
from .ai_abc import AIAbstractClass

from helpers import inject


@inject(config_loader='config_loader')
class AIFacade:
    def __init__(self, provider: str, tone: str = '') -> None:
        self.AI: AIAbstractClass

        config = self.config_loader.load(provider)

        config['name'] = provider

        if tone:
            config['tone'] = tone

        library = config['library']

        if library == 'anthropic':
            self.AI = AnthropicService(config)
        elif library == 'google':
            self.AI = GoogleService(config)
        else:
            self.AI = OpenAIService(config)

    def make_request(self, tone: str, request: str, json: bool = False, stream: bool = False, use_tools: bool = False) \
            -> Union[Generator[str, None, None], str]:
        return self.AI.make_request(tone, request, json, stream, use_tools)

    def update_messages(self, message: str = None, user_message: str = None, full_history: [] = None) -> None:
        self.AI.update_messages(message, user_message, full_history)

    def make_assistant_request(self, stream: bool = False, use_tools: bool = False) -> str:
        return self.AI.make_assistant_request(stream, use_tools)

    def get_name(self) -> str:
        return self.AI.get_name()
