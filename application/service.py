"""Application service that orchestrates domain operations.

The :class:`TodoService` is the single entry-point used by every
presentation layer.  It owns a :class:`~domain.models.TodoList` instance
and exposes high-level use-cases (add / remove / toggle / list).
"""

from __future__ import annotations

from domain.exceptions import DomainError, ItemNotFoundError, ValidationError
from domain.models import FilterType, TodoItem, TodoList


class TodoService:
    """Facade that coordinates domain model operations.

    This service is presentation-agnostic — it knows nothing about
    Streamlit, Gradio, or any other UI toolkit.

    Attributes:
        _todo_list: The underlying domain collection.
    """

    def __init__(self) -> None:
        self._todo_list: TodoList = TodoList()

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------

    def add_item(self, title: str, description: str = "") -> TodoItem:
        """Create and store a new to-do item.

        Args:
            title: Short summary (1-120 characters).
            description: Optional longer description (≤500 characters).

        Returns:
            The newly created :class:`~domain.models.TodoItem`.

        Raises:
            ValidationError: If *title* or *description* are invalid.
        """
        item = TodoItem(title=title.strip(), description=description.strip())
        self._todo_list.add(item)
        return item

    def remove_item(self, item_id: str) -> TodoItem:
        """Remove an existing item by its unique identifier.

        Args:
            item_id: UUID-hex of the item.

        Returns:
            The removed :class:`~domain.models.TodoItem`.

        Raises:
            ItemNotFoundError: If no item with *item_id* exists.
        """
        return self._todo_list.remove(item_id)

    def toggle_item(self, item_id: str) -> TodoItem:
        """Toggle the completed status of an item.

        Args:
            item_id: UUID-hex of the item.

        Returns:
            The toggled :class:`~domain.models.TodoItem`.

        Raises:
            ItemNotFoundError: If no item with *item_id* exists.
        """
        return self._todo_list.toggle(item_id)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def list_items(self, filter_type: FilterType = FilterType.ALL) -> list[TodoItem]:
        """Return items matching *filter_type*.

        Args:
            filter_type: Which subset to return (default: ``ALL``).

        Returns:
            A new list of matching :class:`~domain.models.TodoItem` objects.
        """
        return self._todo_list.filter(filter_type)

    @property
    def total_count(self) -> int:
        """Total number of items."""
        return self._todo_list.count

    @property
    def completed_count(self) -> int:
        """Number of completed items."""
        return self._todo_list.completed_count

    @property
    def pending_count(self) -> int:
        """Number of pending items."""
        return self._todo_list.pending_count

    def get_summary(self) -> str:
        """Return a one-line textual summary of the current state.

        Returns:
            A human-readable summary string.
        """
        return (
            f"Total: {self.total_count} | "
            f"Completed: {self.completed_count} | "
            f"Pending: {self.pending_count}"
        )
