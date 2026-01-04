from enum import Enum
from typing import TypedDict, Required, Union, Literal

from abc import abstractmethod, ABC


class KBaseType(Enum):
    DIRECTORY = 'DIRECTORY'

class DirKnowledgeConfig(TypedDict):
    name: Required[str]
    location: Required[str]
    type: Literal[KBaseType.DIRECTORY]
    kWords: Required[list[str]]

KBaseConfig = Union[DirKnowledgeConfig]

class KBaseService(ABC):
    @abstractmethod
    def __init__(self, config: KBaseConfig) -> None:
        self.config: KBaseConfig = config

    @abstractmethod
    def load_context(self, request: str) -> list[str]:
        raise NotImplementedError
