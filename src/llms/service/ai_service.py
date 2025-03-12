from helpers import load_conf

from llms.service.ai_services import AIAbstractClass, OpenAIService, AnthropicService, GoogleService


class AIService:
    AI: AIAbstractClass = None

    def __init__(self, provider: str, tone: str = '') -> None:
        config = load_conf(provider)

        library = config['library']

        if library == 'anthropic':
            self.AI = AnthropicService(config, tone)
        elif library == 'google':
            self.AI = GoogleService(config, tone)
        else:
            self.AI = OpenAIService(config, tone)

    def make_request(self, tone: str, request: str, json: bool = False, stream: bool = False) -> str:
        return self.AI.make_request(tone, request, json, stream)

    def make_history_request(self, my_messages: [str], other_messages: [[str]], first: bool = False) -> str:
        return self.AI.make_history_request(my_messages, other_messages, first)

    def get_name(self) -> str:
        return self.AI.get_name()
