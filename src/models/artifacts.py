"""Domain models representing files produced by an automation run."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path


class ArtifactKind(StrEnum):
    """The Playwright artifact categories currently understood by the CLI."""

    TRACE = "trace"
    SCREENSHOT = "screenshot"
    VIDEO = "video"
    ERROR_CONTEXT = "error_context"
    STACK_TRACE = "stack_trace"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class Artifact:
    """A single file discovered in an automation-results directory."""

    path: Path
    kind: ArtifactKind
    size_bytes: int


@dataclass(frozen=True, slots=True)
class ArtifactInventory:
    """The complete, deterministic inventory for one test-results directory."""

    root: Path
    artifacts: tuple[Artifact, ...] = field(default_factory=tuple)

    @property
    def total_files(self) -> int:
        """Return the total number of files discovered."""

        return len(self.artifacts)

    def count(self, kind: ArtifactKind) -> int:
        """Return the number of artifacts in a category."""

        return sum(artifact.kind is kind for artifact in self.artifacts)
