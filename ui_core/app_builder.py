"""Agnostic UI orchestration base.

This module provides the :class:`AppBuilder` base class, which
implements the high-level 'recipe' of the Todo Application
independently of any concrete UI framework.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ui_core.interfaces import Button, SelectionInput, UIFactory
from application.service import TodoService


class AppBuilder(ABC):
    """Builds and launches the complete application UI.

    The AppBuilder defines the 'composition recipe' (layout and structure)
    of the application in its :meth:`compose` method.

    Attributes:
        service: The application-layer service.
        factory: The concrete UI factory (Gradio, Streamlit, etc).
        app_name: The visible name of the application.
    """

    def __init__(self, service: TodoService, factory: UIFactory, app_name: str) -> None:
        self.service = service
        self.factory = factory
        self.app_name = app_name

    def compose(self) -> dict[str, Any]:
        """The agnostic recipe to build the entire Todo Application structure.
        
        Returns:
            A dictionary of main widget references for event wiring.
        """
        self.factory.create_header(f"🚀 {self.app_name}").render()
        status = self.factory.create_display(self.service.get_summary()).render()

        widgets: dict[str, Any] = {"status": status}

        with self.factory.create_row():
            cols = self.factory.create_columns([2, 3])
            
            with cols[0]:
                self.factory.create_header("Add Task", level=2).render()
                title_in = self.factory.create_text_input("Task Title", "What needs doing?").render()
                desc_in = self.factory.create_text_area("Description (Optional)").render()
                add_btn = self.factory.create_button("Add Task")
                
                widgets.update({"title_in": title_in, "desc_in": desc_in, "add_btn": add_btn})
                self.wire_add_task(add_btn, title_in, desc_in)

            with cols[1]:
                self.factory.create_header("Tasks", level=2).render()
                from domain.models import FilterType
                filter_sel = self.factory.create_selection(
                    "Filter", 
                    choices=[f.value for f in FilterType],
                    default=FilterType.ALL.value
                )
                filter_rendered = filter_sel.render()
                
                widgets.update({"filter_sel": filter_sel, "filter_rendered": filter_rendered})
                self.wire_filter_change(filter_sel)
                
                # Dynamic Task List component
                task_list = self.factory.create_task_list(self.service, filter_sel)
                task_list.render()
                
        return widgets

    @abstractmethod
    def wire_add_task(self, btn: Button, title_ref: Any, desc_ref: Any) -> None:
        """Framework-specific wiring for adding a task."""
        pass

    @abstractmethod
    def wire_filter_change(self, filter_sel: SelectionInput) -> None:
        """Framework-specific wiring for filter changes."""
        pass

    @abstractmethod
    def build(self) -> Any:
        """Framework entry point."""
        pass

    @abstractmethod
    def launch(self) -> None:
        """Start the application event loop (blocking)."""
        pass
