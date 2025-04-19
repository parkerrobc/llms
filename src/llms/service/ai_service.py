from collections import OrderedDict

from .ai_facade import AIFacade


class AIService(OrderedDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __instantiate_ai(self, model: str, tone: str, key: str) -> None:
        print(f'*** instantiating {model}{' with' + key if key else ''} ***')
        ai_facade = AIFacade(model, tone)
        if key:
            self.__setitem__(key, ai_facade)
        else:
            self.__setitem__(model, ai_facade)

    def get(self, model: str, tone: str = '', key: str = '') -> AIFacade:
        if key and key not in self.keys():
            self.__instantiate_ai(model, tone, key)
        elif not key and model not in self.keys():
            self.__instantiate_ai(model, tone, key)

        ai_facade: AIFacade

        if key:
            ai_facade = self.__getitem__(key)
        else:
            ai_facade = self.__getitem__(model)

        return ai_facade
