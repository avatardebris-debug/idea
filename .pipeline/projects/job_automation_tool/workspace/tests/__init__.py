"""Pytest configuration for job automation tool tests."""

import sys
import pathlib

# Ensure workspace is in path for imports
_ws = pathlib.Path(__file__).parent
if str(_ws) not in sys.path:
    sys.path.insert(0, str(_ws))
