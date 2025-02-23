import json
import sys

from rich.markdown import Markdown
from rich.console import Console

from .classes import Website
from service import OpenAIService

BROCHURE_SCAN_TONE = """
You are an assistant that analyzes the contents of several relevant pages from a company website
and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown.
Include details of company culture, customers and careers/jobs if you have the information.
"""

LINK_SCAN_TONE = """
You are provided with a list of links found on a webpage.
You are able to decide which of the links would be most relevant to include in a brochure about the company,
such as links to an About page, or a Company page, or Careers/Jobs pages.

You should respond in JSON as in this example:

{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page": "url": "https://another.full.url/careers"}
    ]
}

"type" and "url" must be Strings, not an object or array.
"url" must be a valid https url or a full url.
"""


def __create_link_scan_request(website: Website) -> str:
    return f"""
            Here is the list of links on the website of {website.url} - please decide which of these are relevant 
            web links for a brochure about the company, respond with the full https URL in JSON format. 
            Do not include Terms of Service, Privacy, email links.

            Links (some might be relative links):
            {" ".join(website.links)}
            """[:5000]


def __create_brochure_request(website: Website, scan_results: str) -> str:
    return f"""
    You are looking at a company called: {website.title}. 
    Here are the contents of its landing page and other relevant pages; use this information to build a 
    short brochure of the company in markdown.
    
    {scan_results}
    """[:5000]


def __scan_website(website: Website, open_ai_service: OpenAIService) -> str:
    link_scan_request = __create_link_scan_request(website)
    link_scan_results = open_ai_service.make_request(LINK_SCAN_TONE, link_scan_request, True)

    if not link_scan_results.choices:
        print("\nAI request failed\n")
        sys.exit(1)

    links = json.loads(link_scan_results.choices[0].message.content)

    if not links:
        print("\nNo links found\n")
        sys.exit(1)

    link_content: str = ''

    for link in links['links']:
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
    """[:5000]


def __make_brochure(website: Website, scan_results: str, open_ai_service: OpenAIService):
    brochure_request = __create_brochure_request(website, scan_results)
    brochure_response = open_ai_service.make_request(BROCHURE_SCAN_TONE, brochure_request)

    if not brochure_response.choices:
        print("\nAI request failed\n")
        sys.exit(1)

    brochure = brochure_response.choices[0].message.content
    brochure = brochure.replace("```", "").replace("markdown", "")

    console = Console()
    console.print(Markdown(brochure))


def create_brochure(url: str, open_ai_service: OpenAIService) -> None:
    website = Website(url)
    scan_results = __scan_website(website, open_ai_service)
    __make_brochure(website, scan_results, open_ai_service)
