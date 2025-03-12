from collections import OrderedDict

from llms.core.classes import Model


class Battle:
    CHAT_HISTORY: OrderedDict = {}
    MODELS: [Model] = None

    def __init__(self, models: [Model]) -> None:
        self.MODELS = models
        for model in models:
            name = model['name']
            service = model['service']
            first_message = model['firstMessage'] or 'Hello there!'
            self.CHAT_HISTORY.__setitem__(f'{name}-{service.get_name()}', model | {'messages': [first_message]})

    def start_battle(self, number_of_interactions: int) -> None:
        print('******** Battle *******')
        for interaction in range(number_of_interactions):
            print(f'\n**** interaction: {interaction + 1} ****')
            for index, (key, value) in enumerate(self.CHAT_HISTORY.items()):
                name = value['name']
                print(f'\n{name}:')
                messages = value['messages']
                other_messages = [v['messages'] for k, v in self.CHAT_HISTORY.items() if k != key]
                response = (value['service'].make_history_request
                            (messages, other_messages, first=(True if index == 0 else False)))

                new_message: str = ''

                for info in response:
                    print(f'\t{info}')
                    new_message += info

                messages.append(new_message)

                self.CHAT_HISTORY.__setitem__(key, value | {'messages': messages})
