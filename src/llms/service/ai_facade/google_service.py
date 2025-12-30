from typing import Generator

import google.generativeai

from .ai_abc import AIAbstractClass, GoogleConfig


class GoogleService(AIAbstractClass):
    def __init__(self, config: GoogleConfig) -> None:
        super().__init__(config)
        self.MESSAGES = []

        if config['key']:
            google.generativeai.configure(api_key=config['key'])
        else:
            google.generativeai.configure()

        return

    def update_messages(self, use_system_message: bool, system_message: str, assistant_message: str,
                        user_message: str, full_history: list[dict], assistant_thread: bool = False) -> None:
        """
        TODO
        """

    def make_assistant_request(self, json: bool, stream: bool, use_tools: bool) -> Generator[str]:
        pass

    def make_request(self, tone: str, request: str, json: bool, stream: bool, use_tools: bool) \
            -> Generator[str]:

        user_message = (request or self.config['request']) \
            if self.request_char_limit <= 0 \
            else (request or self.config['request'])[:self.request_char_limit]

        method_args: dict = {
            'model_name': self.config['model'],
            'system_instruction': f"{self.tone}. {tone}" if tone else self.tone
        }

        llm = google.generativeai.GenerativeModel(**method_args)

        response = llm.generate_content(user_message)

        yield response.text
