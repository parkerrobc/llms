from typing import Union, Generator

from helpers import inject


@inject(ai_service='ai_service')
class BrochureMaker:
    """
        This class uses AI to create a brochure.
    """

    TONE = """
    You are an assistant that analyzes the contents of several relevant pages from a company
    website and creates a short brochure about the company for prospective customers, investors and recruits.
    Respond in markdown. Include details of company culture, customers and careers/jobs if you have the information.
    """
    REQUEST = """
    You are looking at a company called: {title}.
    Here are the contents of its landing page and other relevant pages; use this information to build a
    short brochure of the company in markdown.
    {details}
    """

    def create_brochure(self, model: str, tone: str, title: str, details: str, stream: bool = False) \
            -> Union[Generator[str, None, None]]:
        """
            creates an AI generated markdown brochure using self.TONE and self.REQUEST

            :param tone:
            :param model:
            :param title: str -> for the title of the brochure
            :param details: str: -> unprocessed information about the brochure
            :param stream: if you want to stream the response

            :return: str -> the brochure as a markdown string
        """
        ai_facade = self.ai_service.get(model)
        tone = f"{self.TONE}  {tone}" if tone else self.TONE
        brochure_request = self.REQUEST.replace('{title}', title).replace('{details}', details)
        brochure_response = ai_facade.make_request(tone, brochure_request, stream=stream)

        yield from map(lambda x: x.replace("markdown", ""), brochure_response)
