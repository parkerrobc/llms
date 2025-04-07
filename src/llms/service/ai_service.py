from typing import Generator, Union

from helpers import load_conf

from llms.service.ai_services import AIAbstractClass, OpenAIService, AnthropicService, GoogleService


class AIService:
    def __init__(self, provider: str, tone: str = '') -> None:
        self.AI: AIAbstractClass

        config = load_conf(provider)

        library = config['library']

        if library == 'anthropic':
            self.AI = AnthropicService(config, tone)
        elif library == 'google':
            self.AI = GoogleService(config, tone)
        else:
            self.AI = OpenAIService(config, tone)

    def make_request(self, tone: str, request: str, json: bool = False, stream: bool = False) \
            -> Union[Generator[str, None, None], str]:
        return self.AI.make_request(tone, request, json, stream)

    def update_messages(self, message: str = None, user_message: str = None, full_history: [] = None) -> None:
        self.AI.update_messages(message, user_message, full_history)

    def make_assistant_request(self) -> str:
        return self.AI.make_assistant_request()

    def get_name(self) -> str:
        return self.AI.get_name()
