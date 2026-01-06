from typing import Iterator

from helpers import inject


@inject(provider_factory='provider_factory')
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
            -> Iterator[str]:
        """
            creates an AI generated markdown brochure using self.TONE and self.REQUEST

            :param tone:
            :param model:
            :param title: str -> for the title of the brochure
            :param details: str: -> unprocessed information about the brochure
            :param stream: if you want to stream the response

            :return: str -> the brochure as a markdown string
        """
        print('*** creating brochure ***')
        print(details)
        provider = self.provider_factory.get(model)
        tone = f"{self.TONE}  {tone}" if tone else self.TONE
        brochure_request = self.REQUEST.replace('{title}', title).replace('{details}', details)
        brochure_response = provider.make_request(system_message=tone, request=brochure_request, stream=stream)

        parsed_response = ''

        for chunk in brochure_response:
            parsed_response += chunk

        yield from map(lambda x: x.replace("markdown", ""), parsed_response)
