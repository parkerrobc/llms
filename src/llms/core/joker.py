from llms.service import AIService


class Joker:
    """
        wanna hear a joke? ask this mo-fo
    """

    JOKE_TONE = """
    You are an assistant that is great at telling jokes.
    """
    JOKE_REQUEST = """
    Tell a {joke_type} joke for an audience of {audience}.
    """

    AIService: AIService = None

    TONE: str = ''
    REQUEST: str = ''

    def __init__(self, tone: str, joke_type: str, audience: str, ai_service: AIService) -> None:
        """
        :param tone: -> tone of the joke
        :param ai_service: -> AI service that will make the joke
        """
        self.AI_SERVICE = ai_service
        self.TONE = f"{self.JOKE_TONE} {tone}" if tone else self.JOKE_TONE
        self.REQUEST = self.JOKE_REQUEST.replace('{joke_type}', joke_type).replace('{audience}', audience)

    def tell_joke(self) -> str:
        """
        :return: -> str the joke
        """
        return next(self.AI_SERVICE.make_request(self.TONE, self.REQUEST))
