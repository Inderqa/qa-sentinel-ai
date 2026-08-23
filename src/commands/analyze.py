"""Analysis-command orchestration for the QA Sentinel CLI."""

from pathlib import Path

from rich.console import Console
from rich.table import Table

from src.artifacts import ArtifactDiscoveryError, discover_artifacts
from src.models import ArtifactKind, FailureEvidence
from src.parser import extract_failure_evidence
from src.utils.logger import get_logger

logger = get_logger(__name__)


def run_analysis(path: Path, console: Console) -> bool:
    """Discover input artifacts and render the Phase 1 inventory summary.

    Returns ``True`` when the directory was processed successfully, otherwise
    ``False`` after showing a user-facing validation error.
    """

    try:
        inventory = discover_artifacts(path)
    except ArtifactDiscoveryError as error:
        logger.warning(str(error))
        console.print(f"[red]{error}[/red]")
        return False

    logger.info("Discovered {} artifacts under {}", inventory.total_files, inventory.root)
    console.print(f"Input path: [cyan]{inventory.root}[/cyan]")

    summary = Table(title="Playwright Artifact Inventory")
    summary.add_column("Artifact type", style="cyan")
    summary.add_column("Files", justify="right")
    for kind in ArtifactKind:
        count = inventory.count(kind)
        if count:
            summary.add_row(kind.replace("_", " ").title(), str(count))
    summary.add_row("Total", str(inventory.total_files), style="bold")
    console.print(summary)
    evidence = extract_failure_evidence(inventory)
    _render_evidence_summary(evidence, console)
    logger.info("Extracted structured failure evidence from {} artifacts", inventory.total_files)
    return True


def _render_evidence_summary(evidence: FailureEvidence, console: Console) -> None:
    """Render the bounded, human-readable extraction result for Phase 1."""

    console.rule("[bold cyan]Extracted Failure Evidence[/bold cyan]")
    if evidence.primary_error:
        console.print(f"[bold red]Likely failure message:[/bold red] {evidence.primary_error}")
    else:
        console.print("[yellow]No explicit error message was found in the available text artifacts.[/yellow]")

    if evidence.log_highlights:
        console.print("[bold]Relevant log lines:[/bold]")
        for line in evidence.log_highlights:
            console.print(f"  • {line}")

    if evidence.trace_failures:
        failures = Table(title="Failures Found in Trace")
        failures.add_column("Test artifact folder", style="cyan")
        failures.add_column("Action", style="red")
        failures.add_column("Error")
        for failure in evidence.trace_failures:
            failures.add_row(
                failure.trace_path.parent.name,
                failure.action or "Unknown action",
                failure.error_message,
            )
        console.print(failures)

    if evidence.traces:
        trace_table = Table(title="Trace Metadata")
        trace_table.add_column("Trace")
        trace_table.add_column("Archive files", justify="right")
        trace_table.add_column("Recorded events", justify="right")
        for trace in evidence.traces:
            event_count = str(trace.event_count) if trace.event_count is not None else "not read"
            trace_table.add_row(trace.path.name, str(trace.file_count), event_count)
        console.print(trace_table)

    for warning in evidence.warnings:
        console.print(f"[yellow]Warning: {warning}[/yellow]")

    console.print("[green]Status: Phase 1 evidence extraction complete.[/green]")
