import json

from llms.core.classes import Website

from llms.service import AIService


def process_links(links: json) -> str:
    """
        processes a json object in the following format:
            {
                "links" : [
                    {
                        "type": str,
                        "url": str,
                    }
                ]
            }

        this method uses the urls for all links and fetches the webdata,
        compiles it into a string, and returns said string
    """

    if not links or 'links' not in links:
        return ''

    link_content: str = ''

    for link in links['links']:
        if 'url' not in link or not isinstance(link['url'], str):
            continue

        link_url = link['url']
        link_type = link['type'] if 'type' in link else ''

        link_website = Website(link_url)
        link_content += f"""
            {link_type}
            {link_website.get_contents()}
        """

    return link_content


class WebScanner:
    """
        This class uses AI to scan website data
    """

    SCAN_TONE = """
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
    "url" must be a valid https url.
    """
    SCAN_REQUEST = """
    Here is the list of links on the website of {url} - please decide which of these are relevant
    web links for a brochure about the company, respond with the full https URL in JSON format.
    Do not include Terms of Service, Privacy, email links.
    Links (some might be relative links):
    {links}
    """

    def __init__(self, ai_service: AIService):
        """
        :param ai_service: -> AI service that will scan the website content
        """
        self.AI_SERVICE = ai_service

    def scan_website(self, website: Website) -> str:
        """
        scans a given website using AI and returns details on each important link as a string

        :param website:

        :return: -> str containing details about the website
        """
        scan_request = (self.SCAN_REQUEST
                        .replace('{url}', website.title)
                        .replace('{links}', ", ".join(website.links)))

        scan_results = self.AI_SERVICE.make_request(self.SCAN_TONE, scan_request, True)

        try:
            links = json.loads(next(scan_results))
        except Exception as e:
            print("\nError parsing link scan results: {}\n".format(e))
            return website.get_contents()

        return f"{website.title}  {website.get_contents()}  {process_links(links)}"
