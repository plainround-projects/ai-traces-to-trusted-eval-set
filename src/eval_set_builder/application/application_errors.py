"""Errors raised by application-level checks."""

from __future__ import annotations


class RebuildMismatchError(RuntimeError):
    """Rebuilding the eval set from the same traces and seed did not reproduce the committed manifest."""
