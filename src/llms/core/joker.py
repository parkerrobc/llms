from typing import Generator

from helpers import inject


@inject(provider_factory='provider_factory')
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

    def tell_joke(self, model: str, tone: str, joke_type: str, audience: str) -> Generator[str]:
        """
        :return: -> str the joke
        """
        provider = self.provider_factory.get(model)
        tone = f"{self.TONE} {tone}" if tone else self.TONE
        request = self.REQUEST.replace('{joke_type}', joke_type).replace('{audience}', audience)

        yield provider.make_request(system_message=tone, request=request)
