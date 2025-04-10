from typing import Callable

from rich.console import Console
from rich.markdown import Markdown

import gradio as gr


def display_markdown(brochure: str) -> None:
    console = Console()
    console.print(Markdown(brochure))


def create_request_display(function: Callable, models: [str]) -> None:
    view = gr.Interface(
        fn=function,
        inputs=[
            gr.Textbox(label="Your request:"),
            gr.Dropdown(models, label="Select model:", value="-")
        ],
        outputs=[gr.Markdown(label="Response:")],
        flagging_mode="never"
    )
    view.launch(inbrowser=True)


def create_model_selection_display(function: Callable, models: [str]) -> None:
    view = gr.Interface(
        fn=function,
        inputs=[
            gr.Dropdown(models, label="Select model:", value="-")
        ],
        outputs=[gr.Markdown(label="Selection:")],
        flagging_mode="never"
    )
    view.launch(inbrowser=True)


def create_chat_display(function: Callable) -> None:
    view = gr.ChatInterface(
        fn=function,
        type="messages",
        flagging_mode="never")

    view.launch(inbrowser=True)
