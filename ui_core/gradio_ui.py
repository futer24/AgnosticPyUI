"""Gradio implementation of the UI Abstract Factory.

This module provides concrete Gradio-based widgets and a factory.
Gradio uses a reactive Block system. The :class:`GradioAppBuilder`
configures these blocks and sets up the event-driven logic.
"""

from __future__ import annotations

from typing import Any, Callable

import gradio as gr

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


class GradioTextInput(TextInput):
    def render(self) -> gr.Textbox:
        return gr.Textbox(label=self.label, placeholder=self.placeholder)


class GradioTextArea(TextArea):
    def render(self) -> gr.TextArea:
        return gr.TextArea(label=self.label, placeholder=self.placeholder)


class GradioButton(Button):
    def render(self) -> gr.Button:
        # NOTE: Gradio Button uses 'value' for display text, not 'label'
        return gr.Button(value=self.label)


class GradioCheckbox(Checkbox):
    def render(self) -> gr.Checkbox:
        return gr.Checkbox(label=self.label, value=self.value)


class GradioDisplay(Display):
    def __init__(self, content: str = "", existing_obj: Any = None):
        super().__init__(content)
        self.existing_obj = existing_obj

    def render(self) -> gr.Markdown:
        if self.existing_obj:
            return self.existing_obj
        return gr.Markdown(value=self.content or "Status: Ready")


class GradioSelection(SelectionInput):
    def __init__(
        self,
        label: str,
        choices: list[str] | None = None,
        default: str | None = None,
    ) -> None:
        super().__init__(label, choices, default)
        self._rendered_obj: gr.Dropdown | None = None

    def render(self) -> gr.Dropdown:
        if self._rendered_obj is None:
            self._rendered_obj = gr.Dropdown(
                label=self.label,
                choices=self.choices,
                value=self.default,
            )
        return self._rendered_obj


class GradioHeader(Header):
    def render(self) -> gr.Markdown:
        return gr.Markdown(value=f"{'#' * self.level} {self.label}")


class GradioContainer(Container):
    def __init__(self, scale: int = 1, is_row: bool = False) -> None:
        super().__init__(scale)
        self.is_row = is_row
        self.ctx: Any = None

    def render(self) -> Any:
        return self

    def __enter__(self) -> Container:
        if self.is_row:
            self.ctx = gr.Row()
        else:
            self.ctx = gr.Column(scale=self.scale)
        self.ctx.__enter__()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.ctx:
            self.ctx.__exit__(exc_type, exc_val, exc_tb)


class GradioTaskList(TaskList):
    def __init__(self, service: TodoService, filter_sel: Any, refresh_trigger: Any, status_display: Any) -> None:
        super().__init__(service, filter_sel)
        self.refresh_trigger = refresh_trigger
        self.status_display = status_display

    def render(self) -> None:
        def tick(val: int) -> int:
            return val + 1

        @gr.render(inputs=[self.filter_type, self.refresh_trigger])
        def render_tasks(filter_val: str, _trigger: int) -> None:
            from domain.models import FilterType
            items = self.service.list_items(FilterType(filter_val))
            if not items:
                gr.Markdown(value="ℹ️ No tasks found. Add your first task!")
                return

            for item in items:
                with gr.Row(variant="compact"):
                    cb = gr.Checkbox(value=item.completed, label=" ", show_label=False, container=False, scale=1)
                    with gr.Column(scale=8):
                        gr.Markdown(value=f"**{item.title}**")
                    del_btn = gr.Button(value="🗑️", scale=1, min_width=40)
                    
                    cb.change(
                        fn=lambda i=item.id: self.service.toggle_item(i),
                        inputs=None, outputs=None
                    ).then(
                        fn=lambda: self.service.get_summary(), 
                        outputs=[self.status_display]
                    )
                    
                    del_btn.click(
                        fn=lambda i=item.id: self.service.remove_item(i),
                        inputs=None, outputs=None
                    ).then(
                        fn=lambda: self.service.get_summary(), 
                        outputs=[self.status_display]
                    ).then(
                        fn=tick, inputs=[self.refresh_trigger], outputs=[self.refresh_trigger]
                    )


class GradioUIFactory(UIFactory):
    def __init__(self, trigger_ref: Any = None, status_ref: Any = None):
        self.trigger_ref = trigger_ref
        self.status_ref = status_ref

    def create_text_input(self, label: str, placeholder: str = "") -> TextInput:
        return GradioTextInput(label, placeholder)

    def create_text_area(self, label: str, placeholder: str = "") -> TextArea:
        return GradioTextArea(label, placeholder)

    def create_button(
        self, label: str, on_click: Callable[..., Any] | None = None
    ) -> Button:
        return GradioButton(label, on_click)

    def create_checkbox(self, label: str, value: bool = False) -> Checkbox:
        return GradioCheckbox(label, value)

    def create_display(self, content: str = "") -> Display:
        return GradioDisplay(content, existing_obj=self.status_ref)

    def create_selection(
        self,
        label: str,
        choices: list[str] | None = None,
        default: str | None = None,
    ) -> SelectionInput:
        return GradioSelection(label, choices, default)

    def create_header(self, label: str, level: int = 1) -> Header:
        return GradioHeader(label, level)

    def create_columns(self, scales: list[int]) -> list[Container]:
        return [GradioContainer(scale=s) for s in scales]

    def create_row(self) -> Container:
        return GradioContainer(is_row=True)

    def create_task_list(self, service: TodoService, filter_sel: SelectionInput) -> TaskList:
        return GradioTaskList(service, filter_sel.render(), self.trigger_ref, self.status_ref)


class GradioAppBuilder(AppBuilder):
    """Wires the Gradio UI together using the provided factory."""

    def __init__(self, service: TodoService, factory: UIFactory, app_name: str = "AgnosticPyUI") -> None:
        super().__init__(service, factory, app_name)
        self._refresh_trigger = None
        self._status_widget = None

    def wire_add_task(self, btn: Button, title_ref: Any, desc_ref: Any) -> None:
        def add_task(title: str, desc: str) -> tuple[str, str, str | Any]:
            if not title.strip():
                return gr.update(), gr.update(), "⚠️ Title is required"
            self.service.add_item(title, desc)
            return "", "", self.service.get_summary()

        def tick(val: int) -> int:
            return val + 1

        btn_obj = btn.render()
        btn_obj.click(
            fn=add_task,
            inputs=[title_ref, desc_ref],
            outputs=[title_ref, desc_ref, self._status_widget]
        ).then(
            fn=tick,
            inputs=[self._refresh_trigger],
            outputs=[self._refresh_trigger]
        )

    def wire_filter_change(self, filter_sel: SelectionInput) -> None:
        pass

    def build(self) -> gr.Blocks:
        with gr.Blocks(title=self.app_name) as demo:
            self._refresh_trigger = gr.State(0)
            self._status_widget = gr.Markdown(value=self.service.get_summary())
            
            if isinstance(self.factory, GradioUIFactory):
                self.factory.trigger_ref = self._refresh_trigger
                self.factory.status_ref = self._status_widget

            self.compose()
            
        return demo

    def launch(self) -> None:
        demo = self.build()
        demo.launch()
