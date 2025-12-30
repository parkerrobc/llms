from collections import OrderedDict

from llms.core.classes import Model


class BattleSim:
    def __init__(self, models: list[Model]) -> None:
        self.MODELS: OrderedDict = OrderedDict()

        print(f'\n***** LLM BATTLE *****\n')
        for model in models:
            name = model['name']
            self.MODELS.__setitem__(f'{name}', model)

    def start(self, number_of_interactions: int, first_message: str) -> None:
        for interaction in range(number_of_interactions):
            for i, (key, model) in enumerate(self.MODELS.items()):
                name = model['name']

                if interaction == 0 and i == 0 and first_message:
                    print(f'\n{name.upper()}:\n{first_message}\n')
                    model['service'].update_messages(assistant_message=first_message)

                user_messages = [other_model['response']
                                 for k, other_model in self.MODELS.items()
                                 if k != key and other_model['response'] is not None]

                for user_message in user_messages:
                    if user_message:
                        model['service'].update_messages(user_message=user_message)

                response = model['service'].make_assistant_request()

                parsed_response: str = ''

                for info in response:
                    parsed_response += info

                print(f'\n{name.upper()}:\n{parsed_response}\n')
                model['service'].update_messages(assistant_message=parsed_response, assistant_thread=True)

                self.MODELS.__setitem__(key, model | {'response': parsed_response})
