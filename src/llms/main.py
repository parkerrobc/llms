from argparse import Namespace

from service import OpenAIService
from helpers import Config

from .core.webscanner import WebScanner


def create_brochure_using_ai(config: Config, args: Namespace) -> None:
    open_ai_service = OpenAIService(args, config)
    web_scanner = WebScanner(args.tone, open_ai_service)
    web_scanner.create_brochure(args.url)
