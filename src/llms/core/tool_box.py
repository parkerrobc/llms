import json

from llms.core.classes import Website
from llms.core import WebScanner, BrochureMaker, Joker

from helpers import inject, view_user_conf

models = ['-'] + view_user_conf()


@inject(ai_service='ai_service')
class ToolBox:

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
        ai_facade = self.ai_service.get(model)
        response = ai_facade.make_request(tone='', request=request)

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

    __scan_website_function = {
        "name": "scan_website",
        "description": "Scans a website and returns all of the important details including relevant links and "
                       "information. Call this whenever you need to know the details about a website, for example when "
                       "someone asks 'can you tell me about <url>?'. You should only call this when someone "
                       "explicitly enters a valid https url.",
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
        "simple_request": simple_request,
        "create_brochure": create_brochure,
        "scan_website": scan_website,
        "tell_joke": tell_joke,
    }

    tools = [
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

    def handle_tool_call(self, tool_call_id: str, function: str, args: str) -> dict[str, str]:
        arguments = json.loads(args)

        if function not in self.__functions:
            return {
                "tool_call_id": tool_call_id,
                "role": "tool",
                "name": function,
                "content": 'no tool found'
            }

        tool_response = self.__functions[function](self, **arguments)

        response = {
            "tool_call_id": tool_call_id,
            "role": "tool",
            "name": function,
            "content": tool_response
        }

        return response
