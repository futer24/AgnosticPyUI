"""Application layer for the AgnosticPyUI project.

Provides the :class:`TodoService` that orchestrates domain-model
operations for the upper (presentation) layers.
"""

from application.service import TodoService

__all__: list[str] = ["TodoService"]
