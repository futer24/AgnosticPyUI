"""Domain layer for the AgnosticPyUI project.

Contains core business models and custom exceptions that are independent
of any presentation framework.
"""

from domain.exceptions import (
    DomainError,
    DuplicateItemError,
    ItemNotFoundError,
    ValidationError,
)
from domain.models import TodoItem, TodoList

__all__: list[str] = [
    "DomainError",
    "DuplicateItemError",
    "ItemNotFoundError",
    "TodoItem",
    "TodoList",
    "ValidationError",
]
