from typing import TypedDict, Required, NotRequired


class Model(TypedDict):
    provider: Required[str]
    key: Required[str]
    response: NotRequired[str]
