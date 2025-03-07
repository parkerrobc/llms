from llms.service import AIService


class BrochureMaker:
    """
        This class uses AI to create a brochure.
    """

    BROCHURE_TONE = """
    You are an assistant that analyzes the contents of several relevant pages from a company
    website and creates a short brochure about the company for prospective customers, investors and recruits.
    Respond in markdown. Include details of company culture, customers and careers/jobs if you have the information.
    """
    BROCHURE_REQUEST = """
    You are looking at a company called: {title}.
    Here are the contents of its landing page and other relevant pages; use this information to build a
    short brochure of the company in markdown.
    {details}
    """

    AI_SERVICE: AIService = None

    TONE: str = ''

    def __init__(self, tone: str, ai_service: AIService) -> None:
        """
        :param tone: -> tone of the brochure
        :param ai_service: -> AI service that will create the brochure
        """
        self.AI_SERVICE = ai_service
        self.TONE = f"{self.BROCHURE_TONE}  {tone}" if tone else self.BROCHURE_TONE

    def create_brochure(self, title: str, details: str) -> str:
        """
            creates an AI generated markdown brochure using self.BROCHURE_TONE and self.BROCHURE_REQUEST

            :param title: str -> for the title of the brochure
            :param details: str: -> unprocessed information about the brochure

            :return: str -> the brochure as a markdown string
        """
        brochure_request = self.BROCHURE_REQUEST.replace('{title}', title).replace('{details}', details)
        brochure_response = self.AI_SERVICE.make_request(self.TONE, brochure_request)

        return next(brochure_response).replace("```", "").replace("markdown", "")
