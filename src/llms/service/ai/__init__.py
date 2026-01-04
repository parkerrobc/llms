from .openai_service import OpenAIService
from .anthropic_service import AnthropicService
from .google_service import GoogleService

from .ai_service import Library, AIService, AIConfig


def get_ai_service(config: AIConfig, tone: str = '') -> AIService:
    library = Library[config['library'].upper()]

    if tone:
        config['tone'] = tone

    match library:
        case Library.ANTHROPIC:
            return AnthropicService(config)
        case Library.GOOGLE:
            return GoogleService(config)
        case Library.OPENAI:
            return OpenAIService(config)
