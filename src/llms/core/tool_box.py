import json

from llms.core.classes import Website
from llms.core import WebScanner, BrochureMaker, Joker

from helpers import inject, view_user_conf

models = ['-'] + view_user_conf()


@inject(provider_factory='provider_factory')
class ToolBox:
    __ticket_prices = {"london": "$799", "paris": "$899", "tokyo": "$1400", "berlin": "$499"}

    def get_ticket_price(self, destination_city: str) -> str:
        print(f'*** getting ticket price for {destination_city} ***')
        city = destination_city.lower()
        return self.__ticket_prices.get(city, "Unknown")

    def scan_website(self, model: str, url: str) -> str:
        print(f'*** scanning {url} with {model} ***')
        website = Website(url)
        web_scanner = WebScanner()
        scan_results = web_scanner.scan_website(model, website)
        return scan_results

    def create_brochure(self, model: str, url: str, tone: str = None) -> str:
        print(f'*** creating brochure for {url} with {model} and tone {tone} ***')
        website = Website(url)
        web_scanner = WebScanner()
        brochure_maker = BrochureMaker()

        scan_results = web_scanner.scan_website(model, website)
        brochure = brochure_maker.create_brochure(model, tone, website.title, scan_results)

        result = ''
        for chunk in brochure:
            result += chunk

        return result

    def simple_request(self, model: str, request: str) -> str:
        print(f'*** asking {request} to {model} ***')
        provider = self.provider_factory.get(model)
        response = provider.make_request(request=request)

        result = ''
        for value in response:
            result += value

        return result


    def tell_joke(self, model: str, joke_type: str, audience: str, tone: str = None) -> str:
        print(f'*** telling a {joke_type} joke to {audience} with an {tone} tone ***')
        joker = Joker()
        response = joker.tell_joke(model, joke_type, audience, tone)

        result = ''
        for value in response:
            result += value

        return result

    __get_ticket_price_function = {
        "name": "get_ticket_price",
        "description": "Get the price of a return ticket to the destination city. "
                       "Call this whenever you need to know the ticket price, for example when a customer asks "
                       "'How much is a ticket to this city'",
        "parameters": {
            "type": "object",
            "properties": {
                "destination_city": {
                    "type": "string",
                    "description": "The city that the customer wants to travel to",
                },
            },
            "required": ["destination_city"],
            "additionalProperties": False
        }
    }

    __scan_website_function = {
        "name": "scan_website",
        "description": "Scans a website and returns all of the important details including relevant links and "
                       "information. Call this whenever you need to know the details about a website, for example when "
                       "someone asks 'can you tell me about <url>?'. You should only call this when someone "
                       "explicitly enters a valid https <url>. Never call this without a <url> or without a <model>",
        "parameters": {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "enum": models,
                    "description": "This is the model defined in your system content as 'model=<model_name>'",
                    "default": '-'
                },
                "url": {
                    "type": "string",
                    "description": "The url that someone wants to know information about"
                }
            },
            "required": ["model", "url"],
            "additionalProperties": False
        }
    }

    __create_brochure_function = {
        "name": "create_brochure",
        "description": "Scans a website and returns a brochure in markdown. Call this whenever someone wants to "
                       "create a brochure for a website, for example when someone asks 'create a brochure  "
                       "for <url> in a <tone> tone'.",
        "parameters": {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "enum": models,
                    "description": "This is the model defined in your system content as 'model=<model_name>'",
                    "default": '-'
                },
                "url": {
                    "type": "string",
                    "description": "The url that someone wants to know information about"
                },
                "tone": {
                    "type": "string",
                    "description": "The tone of the brochure"
                }
            },
            "required": ["model", "url"],
            "additionalProperties": False
        }
    }

    __simple_request_function = {
        "name": "simple_request",
        "description": "Makes a simple request to another llm or model. Call this whenever a person asks 'could you "
                       "ask <model> about <request>'. You should only use this tool if the words 'could you ask' "
                       "appear exactly in that order and exactly one time.",
        "parameters": {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "enum": models,
                    "description": "This is the model defined in your system content as 'model=<model_name>'",
                    "default": '-'
                },
                "request": {
                    "type": "string",
                    "description": "The request to the model that someone wants to gain understanding from"
                }
            },
            "required": ["model", "request"],
            "additionalProperties": False
        }
    }

    __tell_joke_function = {
        "name": "tell_joke",
        "description": "Creates a joke using parameters. You should call this whenever someone asks 'use <model> to "
                       "tell a <joke_type> in a <tone> tone for an audience of <audience>'; or any variation of "
                       "someone asking for a joke.",
        "parameters": {
            "type": "object",
            "properties": {
                "model": {
                    "type": "string",
                    "enum": models,
                    "description": "This is the model defined in your system content as 'model=<model_name>'",
                    "default": '-'
                },
                "joke_type": {
                    "type": "string",
                    "description": "Type of joke to make for a given audience"
                },
                "tone": {
                    "type": "string",
                    "description": "The tone the joke should be made in"
                },
                "audience": {
                    "type": "string",
                    "description": "The audience of the joke; i.e. who wants to hear the joke"
                }
            },
            "required": ["model", "joke_type", "audience"],
            "additionalProperties": False
        }
    }

    __functions = {
        "get_ticket_price": get_ticket_price,
        "simple_request": simple_request,
        "create_brochure": create_brochure,
        "scan_website": scan_website,
        "tell_joke": tell_joke,
    }

    __tools = [
        {
            "type": "function",
            "function": __get_ticket_price_function
        },
        {
            "type": "function",
            "function": __scan_website_function
        },
        {
            "type": "function",
            "function": __create_brochure_function
        },
        {
            "type": "function",
            "function": __simple_request_function
        },
        {
            "type": "function",
            "function": __tell_joke_function
        }
    ]

    def get_tools(self):
        return self.__tools

    def handle_tool_call(self, function: str, args: str) -> str:
        if function not in self.__functions:
            return ''

        arguments = json.loads(args)

        tool_response = self.__functions[function](self, **arguments)

        return tool_response
