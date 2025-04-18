from helpers import inject


@inject(ai_service='ai_service')
class Joker:
    """
    wanna hear a joke? ask this mo-fo
    """

    TONE = """
    You are an assistant that is great at telling jokes.
    """
    REQUEST = """
    Tell a {joke_type} joke for an audience of {audience}.
    """

    def tell_joke(self, model: str, tone: str, joke_type: str, audience: str) -> str:
        """
        :return: -> str the joke
        """
        ai_facade = self.ai_service.get(model)
        tone = f"{self.TONE} {tone}" if tone else self.TONE
        request = self.REQUEST.replace('{joke_type}', joke_type).replace('{audience}', audience)

        return next(ai_facade.make_request(tone, request))
