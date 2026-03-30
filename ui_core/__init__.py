"""UI core package for the AgnosticPyUI project.

Exposes the abstract interfaces and concrete factory implementations.
"""

from ui_core.interfaces import UIFactory
from ui_core.app_builder import AppBuilder

__all__: list[str] = [
    "AppBuilder",
    "UIFactory",
]
