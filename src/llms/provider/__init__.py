from typing import OrderedDict, TypedDict, Required, Iterator

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
    kbase: KBaseConfig

class Provider(object):
    def __init__(self, config: ProviderConfig, tone: str = '') -> None:
        self.AIService: AIService = get_ai_service(config['aiConfig'], tone)
        self.KBase: KBaseService = get_kbase_service(config['kbase'])

        if not self.KBase:
            self.use_k_base = False
        else:
            self.use_k_base = True

    async def get_context(self, request: str = '') -> str:
        if self.use_k_base:
            return await self.KBase.load_context(request)

        return ''

    async def make_request(self, **kwargs) -> Iterator[str]:
        # Extract and remove the parameters we want to modify
        system_message = kwargs.pop('system_message', '')
        request = kwargs.pop('request', '')

        # Modify system_message if needed
        system_message += await self.get_context(request)

        # Pass everything to the underlying function
        return self.AIService.make_request(
            system_message=system_message,
            request=request,
            **kwargs
        )

    async def update_messages(self, user_message: str, system_message: str = '', *args, **kwargs) -> None:
        system_message += await self.get_context(user_message)
        print(system_message)
        self.AIService.update_messages(user_message=user_message, system_message=system_message, *args, **kwargs)

    def make_assistant_request(self, *args, **kwargs) -> Iterator[str]:
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


