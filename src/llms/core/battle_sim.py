from helpers import inject
from llms.core.classes import Model

@inject(ai_service='ai_service')
class BattleSim:
    def __init__(self, models: list[Model]) -> None:
        self.MODELS: list[Model] = models

        print(f'\n***** LLM BATTLE *****\n')

    def start(self, number_of_interactions: int, first_message: str) -> None:
        for interaction in range(number_of_interactions):
            for i, model in enumerate(self.MODELS):
                key = model['key']
                provider = model['provider']

                if interaction == 0 and i == 0 and first_message:
                    print(f'\n{key.upper()}:\n{first_message}\n')
                    self.ai_service.get(provider, key=key).update_messages(assistant_message=first_message)

                user_messages = [other_model['response']
                                 for j, other_model in enumerate(self.MODELS)
                                 if j != i and other_model['response'] is not None]

                for user_message in user_messages:
                    if user_message:
                        self.ai_service.get(provider, key=key).update_messages(user_message=user_message)

                response = self.ai_service.get(provider, key=key).make_assistant_request()

                parsed_response: str = ''

                for info in response:
                    parsed_response += info

                print(f'\n{key.upper()}:\n{parsed_response}\n')
                self.ai_service.get(provider, key=key).update_messages(assistant_message=parsed_response, assistant_thread=True)

                self.MODELS.__setitem__(i, model | {'response': parsed_response})
