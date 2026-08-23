from pathlib import Path
from zipfile import ZipFile

from src.artifacts import discover_artifacts
from src.parser import extract_failure_evidence


def test_extracts_error_context_log_highlights_and_trace_metadata(tmp_path: Path) -> None:
    failure = tmp_path / "checkout-chromium"
    failure.mkdir()
    (failure / "error-context.md").write_text("# Page snapshot\nThe checkout button was not visible.")
    (failure / "browser-error.log").write_text(
        "INFO starting browser\nTimeoutError: locator('#checkout') exceeded 5000ms\n"
    )
    with ZipFile(failure / "trace.zip", "w") as trace:
        trace.writestr(
            "trace.trace",
            '{"type":"before","callId":"call@1","apiName":"Locator.fill"}\n'
            '{"type":"after","callId":"call@1","error":{"message":"Error: strict mode violation\\nextra detail"}}\n',
        )
        trace.writestr("network.har", "{}")

    evidence = extract_failure_evidence(discover_artifacts(tmp_path))

    assert evidence.primary_error == "Error: strict mode violation"
    assert evidence.error_context == "# Page snapshot\nThe checkout button was not visible."
    assert evidence.log_highlights == ("TimeoutError: locator('#checkout') exceeded 5000ms",)
    assert evidence.traces[0].file_count == 2
    assert evidence.traces[0].event_count == 2
    assert evidence.trace_failures[0].action == "Locator.fill"
    assert evidence.trace_failures[0].error_message == "Error: strict mode violation"
    assert evidence.warnings == ()


def test_reports_corrupt_trace_without_stopping_other_extraction(tmp_path: Path) -> None:
    (tmp_path / "trace.zip").write_text("not a zip")
    (tmp_path / "error-context.md").write_text("Error: the application returned HTTP 500")

    evidence = extract_failure_evidence(discover_artifacts(tmp_path))

    assert evidence.primary_error == "Error: the application returned HTTP 500"
    assert evidence.traces[0].file_count == 0
    assert "Could not inspect trace trace.zip" in evidence.warnings[0]
