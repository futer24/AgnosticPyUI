"""Custom domain exceptions for the AgnosticPyUI project.

All domain-specific errors inherit from :class:`DomainError` so that
upper layers can catch a single base type when they need a blanket
handler.
"""


class DomainError(Exception):
    """Base exception for all domain-layer errors.

    Attributes:
        message: Human-readable description of the error.
    """

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ValidationError(DomainError):
    """Raised when a domain object receives invalid data.

    Examples:
        * An empty title for a ``TodoItem``.
        * A title that exceeds the maximum allowed length.
    """


class ItemNotFoundError(DomainError):
    """Raised when a requested item does not exist in the collection.

    Attributes:
        item_id: The identifier of the missing item.
    """

    def __init__(self, item_id: str) -> None:
        self.item_id = item_id
        super().__init__(f"Item with id '{item_id}' not found.")


class DuplicateItemError(DomainError):
    """Raised when attempting to add an item that already exists.

    Attributes:
        item_id: The identifier of the duplicate item.
    """

    def __init__(self, item_id: str) -> None:
        self.item_id = item_id
        super().__init__(f"Item with id '{item_id}' already exists.")
