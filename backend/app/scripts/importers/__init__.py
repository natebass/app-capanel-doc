"""
Indicator data importers for California School Dashboard.

This package provides parsers for importing accountability indicator data
from various sources:
- CDE Excel files (eladownload2025.xlsx, etc.)
- State assessment TXT files (caret-delimited)
"""

from .base import BaseIndicatorParser
from .cde_parser import CDEParser
from .state_parser import StateParser

__all__ = ["BaseIndicatorParser", "CDEParser", "StateParser"]
