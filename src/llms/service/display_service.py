from rich.console import Console
from rich.markdown import Markdown


def display_markdown(brochure: str) -> None:
    console = Console()
    console.print(Markdown(brochure))
