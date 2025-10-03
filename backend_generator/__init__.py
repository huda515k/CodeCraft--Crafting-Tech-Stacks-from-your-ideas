"""
backend_generator package

This top-level package exposes subpackages like `erd`. It intentionally avoids
import-time side effects by not importing deep modules here.
"""

__version__ = "1.0.0"
__author__ = "CodeCraft Team"

# Public subpackages
__all__ = [
    "erd",
]
