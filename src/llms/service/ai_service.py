from helpers import load_conf

from llms.service.ai_services import AIProtocol, OpenAIService


class AIService:
    AI: AIProtocol = None

    def __init__(self, provider: str, request_char_limit: int):
        config = load_conf(provider)

        library = config['library']

        if library == 'openai':
            self.AI = OpenAIService(config, request_char_limit)
        else:
            self.AI = OpenAIService(config, request_char_limit)

        self.AI.initialize()

    def make_request(self, tone: str, request: str, json: bool = False, stream: bool = False):
        return self.AI.make_request(tone, request, json, stream)
