from pathlib import Path

import pytest

from src.artifacts import ArtifactDiscoveryError, discover_artifacts
from src.models import ArtifactKind


def test_discovers_and_classifies_playwright_artifacts(tmp_path: Path) -> None:
    failed_test = tmp_path / "example-test-chromium"
    failed_test.mkdir()
    for filename in ("trace.zip", "test-failed-1.png", "video.webm", "error-context.md", "browser-error.log", "notes.json"):
        (failed_test / filename).write_text("artifact")

    inventory = discover_artifacts(tmp_path)

    assert inventory.total_files == 6
    assert inventory.count(ArtifactKind.TRACE) == 1
    assert inventory.count(ArtifactKind.SCREENSHOT) == 1
    assert inventory.count(ArtifactKind.VIDEO) == 1
    assert inventory.count(ArtifactKind.ERROR_CONTEXT) == 1
    assert inventory.count(ArtifactKind.STACK_TRACE) == 1
    assert inventory.count(ArtifactKind.OTHER) == 1


def test_rejects_a_missing_or_non_directory_path(tmp_path: Path) -> None:
    with pytest.raises(ArtifactDiscoveryError, match="Directory not found"):
        discover_artifacts(tmp_path / "missing")

    file_path = tmp_path / "file.txt"
    file_path.write_text("not a directory")
    with pytest.raises(ArtifactDiscoveryError, match="Expected a directory"):
        discover_artifacts(file_path)
