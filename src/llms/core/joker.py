import sys

from llms.service import OpenAIService


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

    OPEN_AI_SERVICE: OpenAIService = None

    TONE: str = ''
    REQUEST: str = ''

    def __init__(self, tone: str, joke_type: str, audience: str, open_ai_service: OpenAIService) -> None:
        """
        :param tone: -> tone of the joke
        :param open_ai_service: -> AI that will make the joke
        """
        self.OPEN_AI_SERVICE = open_ai_service
        self.TONE = f"{self.JOKE_TONE} {tone}" if tone else self.JOKE_TONE
        self.REQUEST = self.JOKE_REQUEST.replace('{joke_type}', joke_type).replace('{audience}', audience)
        print(self.REQUEST)

    def tell_joke(self) -> str:
        """
        :return: -> str the joke
        """
        joke_response = self.OPEN_AI_SERVICE.make_request(self.TONE, self.REQUEST)

        if not joke_response.choices:
            print("\nAI request failed\n")
            sys.exit(1)

        return joke_response.choices[0].message.content
