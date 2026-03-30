"""Unit tests for the Gradio-specific factory."""

from unittest.mock import MagicMock
import gradio as gr

from application.service import TodoService
from ui_core.gradio_ui import GradioUIFactory, GradioAppBuilder


def test_factory_creates_gradio_components() -> None:
    factory = GradioUIFactory()
    
    text_in = factory.create_text_input("Label")
    assert isinstance(text_in.render(), gr.Textbox)
    
    btn = factory.create_button("Click")
    assert isinstance(btn.render(), gr.Button)
    
    check = factory.create_checkbox("Done")
    assert isinstance(check.render(), gr.Checkbox)


def test_gradio_builder_initialises_properly() -> None:
    service = TodoService()
    factory = GradioUIFactory()
    builder = GradioAppBuilder(service, factory)
    
    demo = builder.build()
    assert isinstance(demo, gr.Blocks)
    assert demo.title == "AgnosticPyUI"
