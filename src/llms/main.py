from argparse import Namespace

from llms.core import BrochureMaker, WebScanner, Joker
from llms.core.classes import Website

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


def add_config(args: Namespace) -> None:
    add_update_conf(args.file)
    return


def list_config(args: Namespace) -> None:
    file_names = view_user_conf()

    for file_name in file_names:
        print(file_name)

    return
