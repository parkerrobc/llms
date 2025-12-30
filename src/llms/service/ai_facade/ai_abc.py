from abc import abstractmethod, ABC
from typing import TypedDict, NotRequired, Required, Generator


class BaseConfig(TypedDict):
    name: Required[str]
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
    @abstractmethod
    def __init__(self, config: AnthropicConfig | OpenAIConfig | GoogleConfig) -> None:
        self.config: AnthropicConfig | OpenAIConfig | GoogleConfig = config
        self.tone = config['tone']
        self.request_char_limit = config['requestCharLimit'] or 0

    @abstractmethod
    def make_request(self, tone: str, request: str, json: bool, stream: bool, use_tools: bool) -> Generator[str]:
        raise NotImplementedError

    @abstractmethod
    def update_messages(self, use_system_message: bool, system_message: str, assistant_message: str,
                        user_message: str, full_history: list[dict], assistant_thread: bool) -> None:
        raise NotImplementedError

    @abstractmethod
    def make_assistant_request(self, json: bool, stream: bool, use_tools: bool) -> Generator[str]:
        raise NotImplementedError

    def get_name(self) -> str:
        return f'{self.config['library']}-{self.config['model']}'
