from llms.core.classes import Website
from llms.core import WebScanner
from llms.service import AIService


def __scan_website(url: str, ai_service: AIService) -> str:
    website = Website(url)
    web_scanner = WebScanner(ai_service)
    return web_scanner.scan_website(website)


def __simple_request(model: str, request: str) -> str:
    ai_service = AIService(model)
    response = ai_service.make_request(tone='', request=request)

    result = ''
    for value in response:
        result += value

    return result


__scan_website_function = {
    "name": "__scan_website",
    "description": "Scans a website and returns all of the important details including relevant links and "
                   "information. Call this whenever you need to know the details about a website, for example when "
                   "someone asks 'what can you tell me about facebook.com?'",
    "parameters": {
        "type": "object",
        "parameters": {
            "url": {
                "type": "string",
                "description": "The url that someone wants to know information about"
            }
        },
        "required": ["url"],
        "additionalProperties": False
    }
}

__simple_request_function = {
    "name": "__simple_request",
    "description": "Makes a simple request to another llm or model. Call this whenever a person asks 'could you ask "
                   "someone about', for example when someone asks 'could you ask anthropic about this?'",
    "parameters": {
        "type": "object",
        "parameters": {
            "model": {
                "type": "string",
                "description": "The object that someone wants to gain understanding from"
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

__functions = {
    "__simple_request": __simple_request,
    "__scan_website": __scan_website
}

tools = [
    {
        "type": "function",
        "function": __scan_website_function
    },
    {
        "type": "function",
        "function": __simple_request_function
    }
]


def handle_tool_request(function: str, ai_service: AIService, **kwargs) -> str:
    return __functions[function](kwargs, ai_service)




