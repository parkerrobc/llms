from argparse import Namespace
import uuid
from llms.core import ToolBox, BattleSim
from llms.core.classes import Model
from llms.service import (display_markdown,
                          create_request_display,
                          create_chat_display)
from llms.provider import ProviderFactory

from helpers import ConfigLoader, add_update_conf, view_user_conf, container

"""
instantiate dependencies
"""
config_loader = ConfigLoader()
container.register('config_loader', config_loader)

provider_factory = ProviderFactory()
container.register('provider_factory', provider_factory)

tool_box = ToolBox()
container.register('tool_box', tool_box)


def create_brochure(args: Namespace) -> None:
    brochure = tool_box.create_brochure(args.provider, args.url, args.tone)

    display_markdown(brochure.replace("```", ""))

    return


def simple_request(args: Namespace) -> None:
    response = tool_box.simple_request(args.tone, args.request)

    print(response)

    return


def make_joke(args: Namespace) -> None:
    response = tool_box.tell_joke(args.provider, args.tone, args.jokeType, args.audience)

    print(response)

    return


def battle_sim(args: Namespace) -> None:
    models: list[Model] = []

    for provider in [args.provider, *args.models]:
        key = f'{'default' if provider == '-' else provider}-{str(uuid.uuid4())[3::4]}'
        model: Model = {
            'provider': provider,
            'key': key,
            'response': ''
        }
        models.append(model)

    battle = BattleSim(models)
    battle.start(args.numberOfBattles, args.firstMessage)


def interactive(args: Namespace) -> None:
    models = view_user_conf()

    def call_model(request: str, model: str):
        response = provider_factory.get(model).make_request(system_message=args.tone, request=request, stream=True)

        result = ''
        for chunk in response:
            result += chunk
            yield result

    create_request_display(call_model, models)


def chat_bot(args: Namespace) -> None:
    provider = provider_factory.get(name=args.provider)

    async def chat(message, history):
        await provider.update_messages(use_system_message=True, user_message=message, full_history=history)
        response = provider.make_assistant_request(json=False, stream=True, use_tools=False)
        result = ''

        for chunk in response:
            if not chunk:
                continue
            result += chunk.replace('<', '"').replace('>', '"').replace('/', '')
            yield result

    create_chat_display(chat)


def add_config(args: Namespace) -> None:
    add_update_conf(args.file)
    return


def list_config(_args: Namespace) -> None:
    file_names = view_user_conf()

    for file_name in file_names:
        print(file_name)

    return
