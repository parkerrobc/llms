from argparse import Namespace
import uuid

from llms.core import BrochureMaker, WebScanner, Joker
from llms.core.battle import Battle
from llms.core.classes import Website, Model

from llms.service import AIService, display_markdown

from helpers import load_env, add_update_conf, view_user_conf

"""
load environment variables
"""
load_env()


def create_brochure(args: Namespace) -> None:
    ai_service = AIService(args.provider)
    web_scanner = WebScanner(ai_service)
    brochure_maker = BrochureMaker(args.tone, ai_service)
    website = Website(args.url)

    scan_results = web_scanner.scan_website(website)
    brochure = brochure_maker.create_brochure(website.title, scan_results)
    display_markdown(brochure)
    return


def simple_request(args: Namespace) -> None:
    ai_service = AIService(args.provider)
    response = ai_service.make_request(args.tone, args.request)

    for value in response:
        print(f'{value}\n')

    return


def make_joke(args: Namespace) -> None:
    ai_service = AIService(args.provider)
    joker = Joker(args.tone, args.jokeType, args.audience, ai_service)

    joke = joker.tell_joke()

    print(joke)
    return


def battle(args: Namespace) -> None:
    ai_service = AIService(args.provider)
    start_name = f'{'default' if args.provider == '-' else args.provider}-{str(uuid.uuid4())[3::4]}-{ai_service.get_name()}'
    models: [Model] = [{'name': start_name, 'service': ai_service, 'firstMessage': args.firstMessage}]

    for model in args.models:
        model_service = AIService(model)
        name = f'{'default' if model == '-' else model}-{str(uuid.uuid4())[3::4]}-{model_service.get_name()}'
        models.append({'name': name, 'service': model_service, 'firstMessage': ''})

    battle = Battle(models)
    battle.start_battle(args.numberOfBattles)


def add_config(args: Namespace) -> None:
    add_update_conf(args.file)
    return


def list_config(args: Namespace) -> None:
    file_names = view_user_conf()

    for file_name in file_names:
        print(file_name)

    return
