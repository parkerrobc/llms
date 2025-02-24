import json
import sys

from rich.markdown import Markdown
from rich.console import Console

from helpers import Config
from service import OpenAIService

from .classes import Website


class WebScanner:
    CONFIG_FILE = 'webscanner.properties'
    LINK_EXAMPLE = """
    {
            "links": [
                {"type": "about page", "url": "https://full.url/goes/here/about"},
                {"type": "careers page": "url": "https://another.full.url/careers"}
            ]
    }
    """

    OPEN_AI_SERVICE: OpenAIService = None
    CONFIG: Config = None

    TONE: str = ''

    def __init__(self, tone: str, open_ai_service: OpenAIService):
        self.CONFIG = Config(self.CONFIG_FILE)
        self.OPEN_AI_SERVICE = open_ai_service
        self.TONE = tone or ''

    def create_brochure(self, url: str) -> None:
        brochure_config = self.CONFIG.dict['BROCHURE']
        website = Website(url)
        link_scan_results = self.__scan_links(website, brochure_config)
        brochure = self.__make_brochure(website.title, link_scan_results, brochure_config)
        self.__display_brochure(brochure)

    def __scan_links(self, website: Website, brochure_config: dict) -> str:
        link_scan_tone = (brochure_config['link_scan_tone']
                          .replace('{tone}', self.TONE)
                          .replace('{example}', self.LINK_EXAMPLE))
        link_scan_request = (brochure_config['link_scan_request']
                             .replace('{url}', website.title)
                             .replace('{links}', ", ".join(website.links)))[:5000]

        link_scan_results = self.OPEN_AI_SERVICE.make_request(link_scan_tone, link_scan_request, True)

        if not link_scan_results.choices:
            print("\nAI request failed\n")
            sys.exit(1)

        try:
            links = json.loads(link_scan_results.choices[0].message.content)
        except Exception as e:
            print("\nError parsing link scan results: {}\n".format(e))
            return website.get_contents()

        if not links:
            return website.get_contents()

        link_content: str = ''

        if 'links' not in links:
            return website.get_contents()

        for link in links['links']:
            if 'url' not in link:
                continue

            url = link['url']

            if not isinstance(url, str):
                continue

            link_website = Website(link['url'])
            link_content += f"""
                    {link['type']}
                    {link_website.get_contents()}
                """

        return f"""
            Landing Page: {website.get_contents()}
            {link_content}
        """

    def __make_brochure(self, title: str, link_scan_results: str, brochure_config: dict):
        brochure_tone = (brochure_config['brochure_tone']
                         .replace('{tone}', self.TONE))
        brochure_request = (brochure_config['brochure_request']
                            .replace('{title}', title)
                            .replace('{scan_results}', link_scan_results))[:5000]

        brochure_response = self.OPEN_AI_SERVICE.make_request(brochure_tone, brochure_request)

        if not brochure_response.choices:
            print("\nAI request failed\n")
            sys.exit(1)

        brochure = brochure_response.choices[0].message.content
        return brochure.replace("```", "").replace("markdown", "")

    def __display_brochure(self, brochure: str) -> None:
        console = Console()
        console.print(Markdown(brochure))
