from argparse import Namespace

from service import OpenAIService
from helpers import Config

from .core.webscanner import create_brochure

def create_brochure_using_ai(config: Config, args: Namespace) -> None:
    open_ai_service = OpenAIService(args, config)
    create_brochure(args.url, open_ai_service)
