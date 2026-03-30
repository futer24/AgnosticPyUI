"""Streamlit implementation of the UI Abstract Factory.

This module provides concrete Streamlit-based widgets and a factory.
"""

from __future__ import annotations

from typing import Any, Callable

import streamlit as st

from application.service import TodoService
from domain.models import FilterType
from ui_core.interfaces import (
    Button,
    Checkbox,
    Container,
    Display,
    Header,
    SelectionInput,
    TaskList,
    TextArea,
    TextInput,
    UIFactory,
)
from ui_core.app_builder import AppBuilder


class StreamlitTextInput(TextInput):
    def render(self) -> str:
        return st.text_input(
            label=self.label, 
            placeholder=self.placeholder,
            key=f"st_text_{self.label}"
        )


class StreamlitTextArea(TextArea):
    def render(self) -> str:
        return st.text_area(
            label=self.label, 
            placeholder=self.placeholder,
            key=f"st_area_{self.label}"
        )


class StreamlitButton(Button):
    def render(self) -> bool:
        return st.button(label=self.label, key=f"st_btn_{self.label}")


class StreamlitCheckbox(Checkbox):
    def render(self) -> bool:
        return st.checkbox(label=self.label, value=self.value, key=f"st_chk_{self.label}")


class StreamlitDisplay(Display):
    def render(self) -> None:
        st.info(self.content or "Status: Ready")


class StreamlitHeader(Header):
    def render(self) -> None:
        if self.level == 1:
            st.title(self.label)
        elif self.level == 2:
            st.header(self.label)
        elif self.level == 3:
            st.subheader(self.label)
        else:
            st.markdown(f"{'#' * self.level} {self.label}")


class StreamlitSelection(SelectionInput):
    def render(self) -> str:
        return st.selectbox(
            label=self.label,
            options=self.choices,
            index=self.choices.index(self.default) if self.default in self.choices else 0,
            key=f"st_sel_{self.label}"
        )


class StreamlitContainer(Container):
    def __init__(self, scale: int = 1, col_obj: Any = None) -> None:
        super().__init__(scale)
        self.col_obj = col_obj

    def render(self) -> Any:
        return self

    def __enter__(self) -> Container:
        if self.col_obj:
            self.col_obj.__enter__()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.col_obj:
            self.col_obj.__exit__(exc_type, exc_val, exc_tb)


class StreamlitTaskList(TaskList):
    def render(self) -> None:
        from domain.models import FilterType
        items = self.service.list_items(FilterType(self.filter_type.default))
        if not items:
            st.write("No tasks found.")
            return

        for item in items:
            with st.container():
                c1, c2, c3 = st.columns([0.1, 0.7, 0.2])
                checked = c1.checkbox("", value=item.completed, key=f"chk_{item.id}")
                if checked != item.completed:
                    self.service.toggle_item(item.id)
                    st.rerun()
                
                c2.write(f"**{item.title}**" if not item.completed else f"~~{item.title}~~")
                if item.description:
                    c2.caption(item.description)
                
                if c3.button("🗑️", key=f"del_{item.id}"):
                    self.service.remove_item(item.id)
                    st.rerun()


class StreamlitUIFactory(UIFactory):
    def create_text_input(self, label: str, placeholder: str = "") -> TextInput:
        return StreamlitTextInput(label, placeholder)

    def create_text_area(self, label: str, placeholder: str = "") -> TextArea:
        return StreamlitTextArea(label, placeholder)

    def create_button(
        self, label: str, on_click: Callable[..., Any] | None = None
    ) -> Button:
        # Streamlit buttons return bool
        return StreamlitButton(label, on_click)

    def create_checkbox(self, label: str, value: bool = False) -> Checkbox:
        return StreamlitCheckbox(label, value)

    def create_display(self, content: str = "") -> Display:
        return StreamlitDisplay(content)

    def create_selection(
        self,
        label: str,
        choices: list[str] | None = None,
        default: str | None = None,
    ) -> SelectionInput:
        return StreamlitSelection(label, choices, default)

    def create_header(self, label: str, level: int = 1) -> Header:
        return StreamlitHeader(label, level)

    def create_columns(self, scales: list[int]) -> list[Container]:
        st_cols = st.columns(scales)
        return [StreamlitContainer(s, c) for s, c in zip(scales, st_cols)]

    def create_row(self) -> Container:
        return StreamlitContainer()

    def create_task_list(self, service: TodoService, filter_sel: SelectionInput) -> TaskList:
        return StreamlitTaskList(service, filter_sel)


class StreamlitAppBuilder(AppBuilder):
    """Wires the Streamlit UI together using the provided factory."""

    def __init__(self, service: TodoService, factory: UIFactory, app_name: str = "AgnosticPyUI") -> None:
        super().__init__(service, factory, app_name)

    def wire_add_task(self, btn: Button, title_ref: Any, desc_ref: Any) -> None:
        if btn.render():
            if title_ref:
                self.service.add_item(title_ref, desc_ref)
                st.success("Task added!")
                st.rerun()
            else:
                st.error("Title is required")

    def wire_filter_change(self, filter_sel: SelectionInput) -> None:
        # Streamlit rerun is automatic 
        pass

    def build(self) -> None:
        st.set_page_config(page_title=self.app_name)
        
        # Persistent state for the service
        if "service" not in st.session_state:
            st.session_state.service = self.service
        else:
            self.service = st.session_state.service
            
        self.compose()

    def launch(self) -> None:
        self.build()
