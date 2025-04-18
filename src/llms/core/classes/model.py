from typing import TypedDict, Required, NotRequired

from llms.service.ai_facade import AIFacade


class Model(TypedDict):
    name: Required[str]
    service: Required[AIFacade]
    message: NotRequired[str]
