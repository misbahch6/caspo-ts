"""
This module provides utility functions for debugging and warning output.
"""

import sys


def dbg(msg: str) -> None:
    """
    Print a debug message to stderr.

    This function is used for debugging purposes, printing the given message
    directly to the standard error stream.

    Args:
        msg: The debug message to be printed.
    """
    print(msg, file=sys.stderr)


def warning(msg: str) -> None:
    """
    Print a warning message to stderr.

    This function prepends "WARNING: " to the given message and then uses
    the dbg function to print it to stderr.

    Args:
        msg: The warning message to be printed.
    """
    dbg(f"WARNING: {msg}")
