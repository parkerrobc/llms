from typing import TypedDict, Required, NotRequired

from llms.service import AIService


class Model(TypedDict):
    name: Required[str]
    service: Required[AIService]
    firstMessage: NotRequired[str]
