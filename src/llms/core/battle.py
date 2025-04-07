from collections import OrderedDict

from llms.core.classes import Model


class Battle:
    def __init__(self, models: [Model]) -> None:
        self.MODELS: OrderedDict = OrderedDict()

        print(f'\n***** LLM BATTLE *****\n')
        for model in models:
            name = model['name']
            self.MODELS.__setitem__(f'{name}', model)

    def start_battle(self, number_of_interactions: int) -> None:
        for interaction in range(number_of_interactions):
            for index, (key, value) in enumerate(self.MODELS.items()):
                name = value['name']

                if interaction == 0 and index == 0:
                    message = value['message']
                    print(f'\n{name.upper()}:\n{message}\n')
                    value['service'].update_messages(message=message)
                    continue

                user_messages = [v['message'] if v['message'] else None
                                 for i, (k, v) in
                                 enumerate(self.MODELS.items()) if i != index and i > index]
                user_messages = user_messages + [v['message'] if v['message'] else None
                                                 for i, (k, v) in
                                                 enumerate(self.MODELS.items()) if i != index and i < index]

                for user_message in user_messages:
                    if user_message:
                        value['service'].update_messages(user_message=user_message)

                response = value['service'].make_assistant_request()

                new_message: str = ''

                for info in response:
                    new_message += info

                print(f'\n{name.upper()}:\n{new_message}\n')
                value['service'].update_messages(message=new_message)

                self.MODELS.__setitem__(key, value | {'message': new_message})
