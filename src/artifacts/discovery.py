"""Discovery of Playwright execution artifacts without interpreting their contents."""

from __future__ import annotations

from pathlib import Path

from src.models.artifacts import Artifact, ArtifactInventory, ArtifactKind


class ArtifactDiscoveryError(ValueError):
    """Raised when a requested artifact directory cannot be inspected."""


def discover_artifacts(root: Path) -> ArtifactInventory:
    """Build an inventory of files beneath a Playwright test-results directory.

    Discovery is deliberately content-agnostic. Parsing and classification belong
    to later pipeline stages, which keeps this boundary easy to extend and test.
    """

    resolved_root = root.expanduser().resolve()
    if not resolved_root.exists():
        raise ArtifactDiscoveryError(f"Directory not found: {resolved_root}")
    if not resolved_root.is_dir():
        raise ArtifactDiscoveryError(f"Expected a directory: {resolved_root}")

    artifacts = tuple(
        Artifact(path=path, kind=classify_artifact(path), size_bytes=path.stat().st_size)
        for path in sorted(resolved_root.rglob("*"))
        if path.is_file()
    )
    return ArtifactInventory(root=resolved_root, artifacts=artifacts)


def classify_artifact(path: Path) -> ArtifactKind:
    """Classify a common Playwright artifact by its conventional filename."""

    name = path.name.lower()
    suffix = path.suffix.lower()

    if name == "trace.zip":
        return ArtifactKind.TRACE
    if suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        return ArtifactKind.SCREENSHOT
    if suffix in {".webm", ".mp4"}:
        return ArtifactKind.VIDEO
    if name == "error-context.md":
        return ArtifactKind.ERROR_CONTEXT
    if suffix in {".txt", ".log"} and any(token in name for token in ("error", "stack", "trace")):
        return ArtifactKind.STACK_TRACE
    return ArtifactKind.OTHER
