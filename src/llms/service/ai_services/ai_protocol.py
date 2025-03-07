from abc import abstractmethod
from typing import Protocol


class AIProtocol(Protocol):
    CONFIG: dict = None

    DEFAULT_TONE: str
    DEFAULT_REQUEST: str

    MODEL: str
    REQUEST_CHAR_LIMIT: int = 0

    def __init__(self, config: dict, request_char_limit: int) -> None:
        self.CONFIG = config
        self.DEFAULT_TONE = config['tone']
        self.DEFAULT_REQUEST = config['request']
        self.REQUEST_CHAR_LIMIT = config['requestCharLimit'] or request_char_limit or 100000
        self.MODEL = config['model']

    @abstractmethod
    def initialize(self) -> None: raise NotImplementedError

    @abstractmethod
    def make_request(self, tone: str, request: str, json: bool, stream: bool) -> str: raise NotImplementedError

