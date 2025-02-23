import argparse


class Arguments:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--custom", action=argparse.BooleanOptionalAction,
                            help="connects to llm with [CUSTOM_AI] in app.properties\n"
                                 "\tllm must be compatible OpenAI libraries\n"
                                 "default will connect to OpenAI directly using [OPEN_AI] config"
                                 "in app.properties or .env file with OPEN_API_KEY")
        parser.add_argument("-m", "--model", type=str,
                            help="language model to use.\n"
                                 "\tex:\n"
                                 "\t\t-m llama3.2")
        parser.add_argument("-r", "--request", type=str,
                            help="request you want to send to the llm.\n"
                                 "\tex:\n"
                                 "\t\t-r 'Help me understand why puppies eat things they aren't supposed to'")
        parser.add_argument("-t", "--tone", type=str, nargs='?',
                            help="tone that the model will respond with.\n"
                                 "\tex:\n"
                                 "\t\t-t 'Being a pretentious ass-hat, you are disgusted with mortal men asking, "
                                 "what you believe to be, dumb questions.'")
        parser.add_argument("--createBrochure", action=argparse.BooleanOptionalAction,
                            help="creates brochure using llm")
        parser.add_argument("--url", type=str, nargs='?',
                            help="url to process")

        self.parser = parser

    def get_parser(self) -> argparse.ArgumentParser:
        return self.parser
