from abc import abstractmethod, ABC
from typing import TypedDict, NotRequired, Required


class BaseConfig(TypedDict):
    tone: Required[str]
    request: Required[str]
    model: Required[str]
    library: Required[str]


class AnthropicConfig(BaseConfig, TypedDict):
    requestCharLimit: NotRequired[int]
    maxTokens: Required[int]
    temperature: Required[int]
    baseUrl: NotRequired[str]
    key: NotRequired[str]


class OpenAIConfig(BaseConfig, TypedDict):
    requestCharLimit: NotRequired[int]
    maxTokens: NotRequired[int]
    temperature: NotRequired[int]
    baseUrl: NotRequired[str]
    key: NotRequired[str]


class GoogleConfig(BaseConfig, TypedDict):
    requestCharLimit: NotRequired[int]
    maxTokens: NotRequired[int]
    temperature: NotRequired[int]
    baseUrl: NotRequired[str]
    key: NotRequired[str]


class AIAbstractClass(ABC):
    config: AnthropicConfig | OpenAIConfig = None

    @abstractmethod
    def __init__(self, config: AnthropicConfig | OpenAIConfig | GoogleConfig, tone: str = '') -> None:
        self.config = config
        self.tone = tone or config['tone']
        self.request_char_limit = config['requestCharLimit'] or 0

    @abstractmethod
    def make_request(self, tone: str, request: str, json: bool, stream: bool) -> str:
        raise NotImplementedError

    @abstractmethod
    def make_history_request(self, my_messages: [str], other_messages: [[str]], first: bool) -> str:
        raise NotImplementedError

    def get_name(self) -> str:
        return f'{self.config['library']}-{self.config['model']}'
