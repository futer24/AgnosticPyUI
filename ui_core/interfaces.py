"""Abstract interfaces for the UI-agnostic Abstract Factory pattern.

This module defines the pure contracts that every concrete UI backend
must fulfil. Business logic and orchestrators depend *only* on these
abstractions, never on a specific framework.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Callable

from application.service import TodoService


# ======================================================================
# Component abstractions
# ======================================================================


class UIComponent(ABC):
    """Base class for every renderable UI widget."""

    @abstractmethod
    def render(self) -> Any:
        """Materialise the component in the chosen framework.

        Returns:
            A framework-specific widget object, or ``None`` for
            side-effect-only renderers (e.g. Streamlit).
        """


class TextInput(UIComponent):
    """A single-line text input widget."""
    def __init__(self, label: str, placeholder: str = "") -> None:
        self.label = label
        self.placeholder = placeholder


class TextArea(UIComponent):
    """A multi-line text area widget."""
    def __init__(self, label: str, placeholder: str = "") -> None:
        self.label = label
        self.placeholder = placeholder


class Button(UIComponent):
    """A clickable button."""
    def __init__(self, label: str, on_click: Callable[..., Any] | None = None) -> None:
        self.label = label
        self.on_click = on_click


class Checkbox(UIComponent):
    """A boolean checkbox."""
    def __init__(self, label: str, value: bool = False) -> None:
        self.label = label
        self.value = value


class Display(UIComponent):
    """A read-only text display / status area."""
    def __init__(self, content: str = "") -> None:
        self.content = content


class Header(UIComponent):
    """A heading or title."""
    def __init__(self, label: str, level: int = 1) -> None:
        self.label = label
        self.level = level


class SelectionInput(UIComponent):
    """A dropdown / radio selection widget."""
    def __init__(
        self,
        label: str,
        choices: list[str] | None = None,
        default: str | None = None,
    ) -> None:
        self.label = label
        self.choices: list[str] = choices or []
        self.default = default or (self.choices[0] if self.choices else "")


class Container(UIComponent):
    """A container for multiple components."""
    def __init__(self, scale: int = 1) -> None:
        self.scale = scale

    @abstractmethod
    def __enter__(self) -> Container:
        """Enables context manager usage for layouts."""

    @abstractmethod
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Closes the layout scope."""


class TaskList(UIComponent):
    """A dynamic list of tasks."""
    def __init__(self, service: TodoService, filter_type: Any) -> None:
        self.service = service
        self.filter_type = filter_type


# ======================================================================
# Abstract Factory
# ======================================================================


class UIFactory(ABC):
    """Abstract Factory that creates UI components.

    Each concrete factory (Gradio, Streamlit, …) overrides every
    ``create_*`` method to return framework-specific widgets.
    """

    @abstractmethod
    def create_text_input(self, label: str, placeholder: str = "") -> TextInput:
        """Create a single-line text input."""

    @abstractmethod
    def create_text_area(self, label: str, placeholder: str = "") -> TextArea:
        """Create a multi-line text area."""

    @abstractmethod
    def create_button(
        self, label: str, on_click: Callable[..., Any] | None = None
    ) -> Button:
        """Create a clickable button."""

    @abstractmethod
    def create_checkbox(self, label: str, value: bool = False) -> Checkbox:
        """Create a boolean checkbox."""

    @abstractmethod
    def create_display(self, content: str = "") -> Display:
        """Create a read-only text display."""

    @abstractmethod
    def create_selection(
        self,
        label: str,
        choices: list[str] | None = None,
        default: str | None = None,
    ) -> SelectionInput:
        """Create a selection / dropdown widget."""

    @abstractmethod
    def create_header(self, label: str, level: int = 1) -> Header:
        """Create a headings widget."""

    @abstractmethod
    def create_columns(self, scales: list[int]) -> list[Container]:
        """Create relative columns."""
        pass

    @abstractmethod
    def create_row(self) -> Container:
        """Create a row."""

    @abstractmethod
    def create_task_list(self, service: TodoService, filter_sel: SelectionInput) -> TaskList:
        """Create a dynamic task list."""
