from argparse import Namespace

from llms.core import BrochureMaker, WebScanner
from llms.core.classes import Website

from llms.service import OpenAIService, display_markdown

from helpers import Config

config = Config()


def create_brochure(args: Namespace) -> None:
    open_ai_service = OpenAIService(args, config)
    web_scanner = WebScanner(open_ai_service)
    brochure_maker = BrochureMaker(args.tone, open_ai_service)

    website = Website(args.url)
    scan_results = web_scanner.scan_website(website)
    brochure = brochure_maker.create_brochure(website.title, scan_results)

    display_markdown(brochure)
    return


def simple_request(args: Namespace) -> None:
    open_ai_service = OpenAIService(args, config)
    response = open_ai_service.make_request(args.tone, args.request)
    print(response.choices[0].message.content)
