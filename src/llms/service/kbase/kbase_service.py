from enum import Enum
from typing import TypedDict, Required, Union, Literal

from abc import abstractmethod, ABC

class KBaseType(Enum):
    DIRECTORY = 'DIRECTORY'
    VECTOR = 'VECTOR'

class BaseConfig(TypedDict):
    name: Required[str]

class DirKnowledgeConfig(BaseConfig):
    name: Required[str]
    location: Required[str]
    type: Literal[KBaseType.DIRECTORY]
    metadata: Required[list[str]]

class VectorStoreConfig(BaseConfig):
    connectionStr: Required[str]
    reRankModel: Required[str]
    topN: Required[int]
    location: Required[str]
    embedModel: Required[str]
    tableName: Required[str]
    metadataJsonColumn: Required[str]
    metadataColumns: Required[list[str]]

KBaseConfig = Union[DirKnowledgeConfig, VectorStoreConfig]

class KBaseService(ABC):
    @abstractmethod
    def __init__(self, config: KBaseConfig) -> None:
        self.config: KBaseConfig = config

    @abstractmethod
    async def load_context(self, request: str) -> str:
        raise NotImplementedError
