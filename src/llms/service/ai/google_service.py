from typing import Iterator

import google.generativeai

from .ai_service import AIService, GoogleConfig


class GoogleService(AIService):
    def __init__(self, config: GoogleConfig) -> None:
        super().__init__(config)
        self.MESSAGES = []

        if config['key']:
            google.generativeai.configure(api_key=config['key'])
        else:
            google.generativeai.configure()

        return

    def update_messages(self, use_system_message: bool = True, system_message: str = '', assistant_message: str = '',
                        user_message: str = '', full_history: list[dict] | None = None, assistant_thread: bool = False) -> None:
        """
        TODO
        """

    def make_assistant_request(self, json: bool = False, stream: bool = False, use_tools: bool = False) -> Iterator[str]:
        pass

    def make_request(self, system_message: str = '', request: str = '', json: bool = False, stream: bool = False, use_tools: bool = False) \
            -> Iterator[str]:

        user_message = (request or self.config['request']) \
            if self.request_char_limit <= 0 \
            else (request or self.config['request'])[:self.request_char_limit]

        method_args: dict = {
            'model_name': self.config['model'],
            'system_instruction': f"{self.tone}. {system_message}" if system_message else self.tone
        }

        llm = google.generativeai.GenerativeModel(**method_args)

        response = llm.generate_content(user_message)

        yield response.text
