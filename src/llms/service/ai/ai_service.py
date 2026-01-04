from abc import abstractmethod, ABC

from enum import Enum
from typing import TypedDict, NotRequired, Required, Generator, Literal, Union


class Library(Enum):
    ANTHROPIC = 'ANTHROPIC'
    GOOGLE = 'GOOGLE'
    OPENAI = 'OPENAI'


class BaseConfig(TypedDict):
    name: Required[str]
    tone: Required[str]
    request: Required[str]
    model: Required[str]


class AnthropicConfig(BaseConfig):
    library: Literal[Library.ANTHROPIC]
    requestCharLimit: NotRequired[int]
    maxTokens: Required[int]
    temperature: Required[int]
    baseUrl: NotRequired[str]
    key: NotRequired[str]


class OpenAIConfig(BaseConfig):
    library: Literal[Library.OPENAI]
    requestCharLimit: NotRequired[int]
    maxTokens: NotRequired[int]
    temperature: NotRequired[int]
    baseUrl: NotRequired[str]
    key: NotRequired[str]


class GoogleConfig(BaseConfig):
    library: Literal[Library.GOOGLE]
    requestCharLimit: NotRequired[int]
    maxTokens: NotRequired[int]
    temperature: NotRequired[int]
    baseUrl: NotRequired[str]
    key: NotRequired[str]


AIConfig = Union[AnthropicConfig, OpenAIConfig, GoogleConfig]


class AIService(ABC):
    @abstractmethod
    def __init__(self, config: AIConfig) -> None:
        self.config: AIConfig = config
        self.tone = config['tone']
        self.request_char_limit = config['requestCharLimit'] or 0

    @abstractmethod
    def make_request(self, system_message: str = '', request: str = '', json: bool = False, stream: bool = False, use_tools: bool = False) -> Generator[
        str]:
        raise NotImplementedError

    @abstractmethod
    def update_messages(self, use_system_message: bool = '', system_message: str = '', assistant_message: str ='',
                        user_message: str ='', full_history: list[dict] = None, assistant_thread: bool = False) -> None:
        raise NotImplementedError

    @abstractmethod
    def make_assistant_request(self, json: bool = False, stream: bool = False, use_tools: bool = False) -> Generator[str]:
        raise NotImplementedError

    def get_name(self) -> str:
        return f'{self.config['library']}-{self.config['model']}'
