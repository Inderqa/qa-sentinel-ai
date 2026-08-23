"""Extract safe, structured evidence from discovered Playwright artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from src.models.artifacts import ArtifactInventory, ArtifactKind
from src.models.evidence import FailureEvidence, TraceFailure, TraceSummary

MAX_TEXT_BYTES = 64_000
MAX_CONTEXT_CHARACTERS = 1_200
MAX_LOG_HIGHLIGHTS = 5
MAX_TRACE_EVENT_BYTES = 10_000_000
MAX_TRACE_EVENTS = 10_000
ERROR_TOKENS = ("error", "exception", "failed", "failure", "timeout", "timed out", "expect")


def extract_failure_evidence(inventory: ArtifactInventory) -> FailureEvidence:
    """Read relevant text and trace metadata from an artifact inventory.

    The parser never modifies artifacts and limits text reads, allowing it to be
    safely used against large test-result directories. It intentionally avoids
    semantic root-cause conclusions; that is the responsibility of Phase 2.
    """

    warnings: list[str] = []
    error_contexts = _read_text_artifacts(inventory, ArtifactKind.ERROR_CONTEXT, warnings)
    log_files = _read_text_artifacts(inventory, ArtifactKind.STACK_TRACE, warnings)

    context = _combine_context(error_contexts)
    log_highlights = tuple(
        line
        for _, text in log_files
        for line in _matching_lines(text)
    )[:MAX_LOG_HIGHLIGHTS]
    trace_inspections = tuple(
        _inspect_trace(artifact.path, warnings)
        for artifact in inventory.artifacts
        if artifact.kind is ArtifactKind.TRACE
    )
    traces = tuple(inspection[0] for inspection in trace_inspections)
    trace_failures = tuple(failure for _, failures in trace_inspections for failure in failures)
    primary_error = next(
        (failure.error_message for failure in trace_failures),
        next(iter(log_highlights), _first_error_line(context)),
    )
    return FailureEvidence(
        primary_error=primary_error,
        error_context=context,
        log_highlights=log_highlights,
        traces=traces,
        trace_failures=trace_failures,
        warnings=tuple(warnings),
    )


def _read_text_artifacts(
    inventory: ArtifactInventory, kind: ArtifactKind, warnings: list[str]
) -> list[tuple[Path, str]]:
    result: list[tuple[Path, str]] = []
    for artifact in inventory.artifacts:
        if artifact.kind is not kind:
            continue
        try:
            with artifact.path.open("rb") as source:
                contents = source.read(MAX_TEXT_BYTES)
            result.append((artifact.path, contents.decode("utf-8", errors="replace")))
        except OSError as error:
            warnings.append(f"Could not read {artifact.path.name}: {error}")
    return result


def _combine_context(contexts: list[tuple[Path, str]]) -> str | None:
    if not contexts:
        return None
    text = "\n\n".join(text.strip() for _, text in contexts if text.strip())
    return text[:MAX_CONTEXT_CHARACTERS] or None


def _matching_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and any(token in line.lower() for token in ERROR_TOKENS)
    ]


def _first_error_line(text: str | None) -> str | None:
    if not text:
        return None
    return next(iter(_matching_lines(text)), None)


def _inspect_trace(path: Path, warnings: list[str]) -> tuple[TraceSummary, tuple[TraceFailure, ...]]:
    """Stream trace events, retaining only failed call metadata and error text."""

    try:
        with ZipFile(path) as trace:
            members = trace.infolist()
            event_file = next((member for member in members if member.filename.endswith("trace.trace")), None)
            event_count = None
            failures: list[TraceFailure] = []
            if event_file is not None:
                event_count, failures = _read_trace_events(trace, event_file.filename, path, warnings)
            return TraceSummary(path=path, file_count=len(members), event_count=event_count), tuple(failures)
    except (BadZipFile, OSError) as error:
        warnings.append(f"Could not inspect trace {path.name}: {error}")
        return TraceSummary(path=path, file_count=0, event_count=None), ()


def _read_trace_events(
    trace: ZipFile, event_filename: str, path: Path, warnings: list[str]
) -> tuple[int, list[TraceFailure]]:
    """Read JSONL events with bounded work and join failed calls to their action."""

    actions_by_call_id: dict[str, str] = {}
    failures: list[TraceFailure] = []
    event_count = 0
    processed_bytes = 0
    with trace.open(event_filename) as events:
        for raw_line in events:
            processed_bytes += len(raw_line)
            if processed_bytes > MAX_TRACE_EVENT_BYTES or event_count >= MAX_TRACE_EVENTS:
                warnings.append(f"Trace event limit reached for {path.name}; analysis is partial.")
                break
            try:
                event = json.loads(raw_line)
            except json.JSONDecodeError:
                warnings.append(f"Skipped malformed trace event in {path.name}.")
                continue
            event_count += 1
            call_id = event.get("callId")
            if event.get("type") == "before" and call_id and event.get("apiName"):
                actions_by_call_id[call_id] = event["apiName"]
            error = event.get("error")
            if event.get("type") == "after" and isinstance(error, dict) and error.get("message"):
                failures.append(
                    TraceFailure(
                        trace_path=path,
                        action=actions_by_call_id.get(call_id),
                        error_message=_first_line(error["message"]),
                    )
                )
    return event_count, failures


def _first_line(message: str) -> str:
    """Keep CLI output concise while preserving the most useful error summary."""

    return message.splitlines()[0][:MAX_CONTEXT_CHARACTERS]
