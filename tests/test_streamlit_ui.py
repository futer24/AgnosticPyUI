"""Unit tests for the Streamlit-specific factory."""

from unittest.mock import patch, MagicMock
import streamlit as st

from application.service import TodoService
from ui_core.streamlit_ui import StreamlitUIFactory, StreamlitAppBuilder


@patch("streamlit.text_input")
@patch("streamlit.button")
def test_factory_calls_streamlit_functions(mock_btn: MagicMock, mock_text: MagicMock) -> None:
    factory = StreamlitUIFactory()
    
    factory.create_text_input("My Label").render()
    mock_text.assert_called_once()
    
    factory.create_button("My Button").render()
    mock_btn.assert_called_once()


@patch("streamlit.set_page_config")
@patch("streamlit.title")
@patch("streamlit.session_state", spec={})
def test_streamlit_builder_renders(
    mock_session_state: MagicMock, mock_title: MagicMock, mock_config: MagicMock
) -> None:
    service = TodoService()
    factory = StreamlitUIFactory()
    builder = StreamlitAppBuilder(service, factory)

    # Renders without error
    builder.build()
    mock_title.assert_called()
