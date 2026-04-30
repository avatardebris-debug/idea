#!/usr/bin/env python3
"""Test runner for the property alert system."""

import pytest
import sys


def main():
    """Run all tests."""
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-report=xml"
    ])
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
