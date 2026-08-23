"""Structured evidence extracted from a failed automation run."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class TraceSummary:
    """Non-invasive metadata read from one Playwright trace archive."""

    path: Path
    file_count: int
    event_count: int | None


@dataclass(frozen=True, slots=True)
class TraceFailure:
    """A failed Playwright action reconstructed from a trace event stream."""

    trace_path: Path
    action: str | None
    error_message: str


@dataclass(frozen=True, slots=True)
class FailureEvidence:
    """Normalized Phase 1 evidence, ready for later classification and AI use."""

    primary_error: str | None = None
    error_context: str | None = None
    log_highlights: tuple[str, ...] = field(default_factory=tuple)
    traces: tuple[TraceSummary, ...] = field(default_factory=tuple)
    trace_failures: tuple[TraceFailure, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
