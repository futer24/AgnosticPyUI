"""Domain models for the AgnosticPyUI project.

These models encapsulate the core business rules and are completely
independent of any UI framework or persistence mechanism.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

from domain.exceptions import (
    DuplicateItemError,
    ItemNotFoundError,
    ValidationError,
)

_MAX_TITLE_LENGTH: int = 120
_MAX_DESCRIPTION_LENGTH: int = 500


class FilterType(Enum):
    """Supported filter modes for a :class:`TodoList`."""

    ALL = "all"
    COMPLETED = "completed"
    PENDING = "pending"


@dataclass
class TodoItem:
    """A single to-do entry.

    Attributes:
        id: Unique identifier (UUID4 hex string).
        title: Short summary of the task (1-120 chars).
        description: Optional longer description (≤500 chars).
        completed: Whether the task has been finished.
        created_at: UTC timestamp of creation.
    """

    title: str
    description: str = ""
    completed: bool = False
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )

    def __post_init__(self) -> None:
        """Validate invariants after dataclass initialisation."""
        self._validate()

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def toggle(self) -> None:
        """Flip the *completed* flag."""
        self.completed = not self.completed

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _validate(self) -> None:
        """Enforce business rules on field values.

        Raises:
            ValidationError: If any field violates its constraints.
        """
        if not self.title or not self.title.strip():
            raise ValidationError("Title must not be empty.")
        if len(self.title) > _MAX_TITLE_LENGTH:
            raise ValidationError(
                f"Title must not exceed {_MAX_TITLE_LENGTH} characters."
            )
        if len(self.description) > _MAX_DESCRIPTION_LENGTH:
            raise ValidationError(
                f"Description must not exceed {_MAX_DESCRIPTION_LENGTH} characters."
            )


@dataclass
class TodoList:
    """An ordered collection of :class:`TodoItem` objects.

    Attributes:
        items: Internal list of to-do items.
    """

    items: list[TodoItem] = field(default_factory=list)

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------

    def add(self, item: TodoItem) -> None:
        """Append *item* to the list.

        Args:
            item: The item to add.

        Raises:
            DuplicateItemError: If an item with the same *id* already exists.
        """
        if any(existing.id == item.id for existing in self.items):
            raise DuplicateItemError(item.id)
        self.items.append(item)

    def remove(self, item_id: str) -> TodoItem:
        """Remove and return the item identified by *item_id*.

        Args:
            item_id: Unique identifier of the item to remove.

        Returns:
            The removed :class:`TodoItem`.

        Raises:
            ItemNotFoundError: If no item with the given *id* exists.
        """
        for index, item in enumerate(self.items):
            if item.id == item_id:
                return self.items.pop(index)
        raise ItemNotFoundError(item_id)

    def toggle(self, item_id: str) -> TodoItem:
        """Toggle the *completed* flag of the item with *item_id*.

        Args:
            item_id: Unique identifier of the item to toggle.

        Returns:
            The toggled :class:`TodoItem`.

        Raises:
            ItemNotFoundError: If no item with the given *id* exists.
        """
        for item in self.items:
            if item.id == item_id:
                item.toggle()
                return item
        raise ItemNotFoundError(item_id)

    def get(self, item_id: str) -> TodoItem:
        """Return the item identified by *item_id*.

        Args:
            item_id: Unique identifier of the item to retrieve.

        Returns:
            The matching :class:`TodoItem`.

        Raises:
            ItemNotFoundError: If no item with the given *id* exists.
        """
        for item in self.items:
            if item.id == item_id:
                return item
        raise ItemNotFoundError(item_id)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def filter(self, filter_type: FilterType) -> list[TodoItem]:
        """Return items matching *filter_type*.

        Args:
            filter_type: The filter to apply.

        Returns:
            A **new** list of matching items (never the internal list).
        """
        if filter_type == FilterType.COMPLETED:
            return [i for i in self.items if i.completed]
        if filter_type == FilterType.PENDING:
            return [i for i in self.items if not i.completed]
        return list(self.items)

    @property
    def count(self) -> int:
        """Total number of items."""
        return len(self.items)

    @property
    def completed_count(self) -> int:
        """Number of completed items."""
        return sum(1 for i in self.items if i.completed)

    @property
    def pending_count(self) -> int:
        """Number of pending (incomplete) items."""
        return self.count - self.completed_count
