"""Named errors of the eval-set pipeline."""

from __future__ import annotations


class TraceFormatError(ValueError):
    """A trace line is not valid JSON or does not match the trace schema; the message names the reason."""


class LabelingError(ValueError):
    """A label is not one of the four labels in the guide, or two label passes do not cover the same cases."""


class SyntheticGenerationError(RuntimeError):
    """The synthetic step could not produce enough accepted cases from the seeds it was given."""
