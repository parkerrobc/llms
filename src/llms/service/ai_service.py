from helpers import load_conf

from llms.service.ai_services import AIAbstractClass, OpenAIService, AnthropicService, GoogleService


class AIService:
    AI: AIAbstractClass = None

    def __init__(self, provider: str):
        config = load_conf(provider)

        library = config['library']

        if library == 'anthropic':
            self.AI = AnthropicService(config)
        elif library == 'google':
            self.AI = GoogleService(config)
        else:
            self.AI = OpenAIService(config)

    def make_request(self, tone: str, request: str, json: bool = False, stream: bool = False):
        return self.AI.make_request(tone, request, json, stream)
