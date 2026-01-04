from typing import OrderedDict, TypedDict, Required, NotRequired, Generator

from helpers import inject

from llms.service import (
    AIService,
    KBaseService,
    AIConfig,
    KBaseConfig,
    get_ai_service,
    get_kbase_service)


class ProviderConfig(TypedDict):
    aiConfig: Required[AIConfig]
    kbase: NotRequired[list[KBaseConfig]]

class Provider(object):
    def __init__(self, config: ProviderConfig, tone: str = '') -> None:
        self.AIService: AIService = get_ai_service(config['aiConfig'], tone)
        self.KBases: dict[str, KBaseService] = {}
        self.KWords: dict[str, list[str]] = {}

        for kbase in config['kbase']:
            self.KBases[kbase['name'].lower()] = get_kbase_service(kbase)
            for k_word in kbase['kWords']:
                if not k_word in self.KWords:
                    self.KWords[k_word.lower()] = []
                self.KWords[k_word.lower()].append(kbase['name'].lower())

        self.use_k_base = len(self.KBases) > 0
        print(self.KBases, self.KWords)

    def get_context(self, request: str = '') -> str:
        words = request.lower().split()
        k_bases: list[str] = []
        context: list[str] = []
        loaded = set()

        for word in words:
            if word in self.KWords:
                for kbase in [x for x in self.KWords[word] if x not in loaded]:
                    k_bases.append(kbase)
                    loaded.add(kbase)

        for kbase in k_bases:
            context += self.KBases[kbase].load_context(request)

        return '\n\n'.join(context)

    def make_request(self, **kwargs) -> Generator[str]:
        # Extract and remove the parameters we want to modify
        system_message = kwargs.pop('system_message', '')
        request = kwargs.pop('request', '')

        # Modify system_message if needed
        if self.use_k_base:
            system_message += self.get_context(request)

        # Pass everything to the underlying function
        return self.AIService.make_request(
            system_message=system_message,
            request=request,
            **kwargs
        )


    def update_messages(self, user_message: str, system_message: str = '', *args, **kwargs) -> None:
        if self.use_k_base:
            system_message += self.get_context(user_message)
        self.AIService.update_messages(user_message=user_message, system_message=system_message, *args, **kwargs)

    def make_assistant_request(self, *args, **kwargs) -> Generator[str]:
        return self.AIService.make_assistant_request(*args, **kwargs)



@inject(config_loader='config_loader')
class ProviderFactory(OrderedDict):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(args, **kwargs)

    def __instantiate_provider(self, name: str, tone: str, key: str) -> None:
        config: ProviderConfig = self.config_loader.load(name)
        provider: Provider = Provider(config, tone)

        if key:
            self.__setitem__(key, provider)
        else:
            self.__setitem__(name, provider)


    def get(self, name: str, tone: str = '', key: str = '') -> Provider:
        if key and key not in self.keys():
            self.__instantiate_provider(name, tone, key)
        elif not key and name not in self.keys():
            self.__instantiate_provider(name, tone, key)

        provider: Provider

        if key:
            provider = self.__getitem__(key)
        else:
            provider = self.__getitem__(name)

        return provider


