"""
===============================================================================
Module: src.main
===============================================================================

Purpose
-------
This module serves as the application entry point for QA Sentinel AI.

It is responsible for bootstrapping the command-line interface (CLI) and
starting the application. It does not contain any business logic or
domain-specific implementation.

Why This Module Exists
----------------------
Every application needs a single, well-defined entry point.

The responsibility of this module is to initialize the CLI framework,
register available commands, and transfer control to the appropriate
command implementation.

Keeping the entry point lightweight makes the application easier to
maintain, test, and extend as additional commands are introduced.

Responsibilities
----------------
- Initialize the Typer CLI application.
- Register all CLI commands.
- Start the application lifecycle.
- Delegate execution to command modules.

Out of Scope
------------
This module MUST NOT contain:

- Playwright artifact discovery
- Artifact parsing
- AI reasoning
- Report generation
- Configuration validation
- Business logic

Those responsibilities belong to their respective modules.

Architecture
------------
                    main.py
                        │
                        ▼
                   CLI Commands
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
    parser         classifier        reports

main.py acts only as an orchestrator and should never become a place
where application logic is implemented.

Impact
------
Since this is the application's entry point, changes here affect the
startup process of the entire application.

Any modifications should preserve backward compatibility for CLI users.

Author
------
QA Sentinel AI Contributors

===============================================================================
"""
from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def analyze(
    path: Path = typer.Option(
        ...,
        "--path",
        "-p",
        help="Path to the Playwright test results directory.",
    )
):
    """Analyze a Playwright test results directory."""

    console.rule("[bold cyan]QA Sentinel AI[/bold cyan]")

    if not path.exists():
        console.print(f"[red]Directory not found:[/red] {path}")
        raise typer.Exit(code=1)

    console.print("[green]✓ Project initialized[/green]")
    console.print(f"Input Path : {path.resolve()}")
    console.print("[yellow]Status     : Ready for analysis[/yellow]")


if __name__ == "__main__":
    app()