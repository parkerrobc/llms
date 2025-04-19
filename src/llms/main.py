from argparse import Namespace
import uuid

from llms.core import ToolBox
from llms.core.battle_sim import BattleSim
from llms.core.classes import Model

from llms.service import (AIService,
                          display_markdown,
                          create_request_display,
                          create_chat_display)

from helpers import ConfigLoader, add_update_conf, view_user_conf, container

"""
instantiate dependencies
"""
config_loader = ConfigLoader()
container.register('config_loader', config_loader)

ai_service = AIService()
container.register('ai_service', ai_service)

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
    joke = tool_box.tell_joke(args.provider, args.tone, args.jokeType, args.audience)

    print(joke)

    return


def battle_sim(args: Namespace) -> None:
    start_name = f'{'default' if args.provider == '-' else args.provider}-{str(uuid.uuid4())[3::4]}'
    ai_facade = ai_service.get(model=args.provider, key=start_name)
    models: [Model] = [
        {'name': f'{start_name}-{ai_facade.get_name()}', 'service': ai_facade, 'message': args.firstMessage}]

    for model in args.models:
        name = f'{'default' if model == '-' else model}-{str(uuid.uuid4())[3::4]}'
        model_service = ai_service.get(model=model, key=name)
        models.append({'name': f'{name}-{model_service.get_name()}', 'service': model_service, 'message': ''})

    battle = BattleSim(models)
    battle.start(args.numberOfBattles)


def interactive(args: Namespace) -> None:
    models = view_user_conf()

    def call_model(request: str, model: str):
        response = ai_service.get(model).make_request(tone=args.tone, request=request, stream=True)

        result = ''
        for chunk in response:
            result += chunk
            yield result

    create_request_display(call_model, models)


def chat_bot(args: Namespace) -> None:
    ai_facade = ai_service.get(model=args.provider)

    def chat(message, history):
        ai_facade.update_messages(user_message=message, full_history=history)
        response = ai_facade.make_assistant_request(stream=False, use_tools=True)
        result = ''

        for chunk in response:
            result += chunk
            yield result

    create_chat_display(chat)


def add_config(args: Namespace) -> None:
    add_update_conf(args.file)
    return


def list_config(args: Namespace) -> None:
    file_names = view_user_conf()

    for file_name in file_names:
        print(file_name)

    return
