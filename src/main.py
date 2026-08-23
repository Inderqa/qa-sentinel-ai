"""
===============================================================================
Module: src.main
===============================================================================

Purpose
-------
Entry point for the QA Sentinel AI application.

This module is responsible for bootstrapping the command-line interface (CLI),
initializing application-wide services such as logging, and delegating execution
to the appropriate command handlers.

Why This Module Exists
----------------------
Every application requires a single entry point responsible for initializing
shared infrastructure before any business logic is executed.

Responsibilities
----------------
- Initialize application logging.
- Configure the CLI.
- Validate user input.
- Delegate execution to the analysis workflow.

Out of Scope
------------
This module MUST NOT contain:

- Artifact discovery
- Artifact parsing
- AI reasoning
- Report generation
- Business logic

Architecture
------------
                   main.py
                      │
                      ▼
          configure_logging()
                      │
                      ▼
               CLI Commands
                      │
                      ▼
        Analysis / Parser / Reports

Impact
------
Changes to this module affect the application startup lifecycle.

Version History
---------------
v0.1.0
    Initial implementation.
===============================================================================
"""
from pathlib import Path
import typer

from rich.console import Console
from src.commands.analyze import run_analysis
from src.utils.logger import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)
app = typer.Typer(no_args_is_help=True)
console = Console()


@app.callback()
def main() -> None:
    """Analyze automated-test evidence and produce QA insights."""


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

    logger.info("QA Sentinel AI started.")
    logger.info(f"Artifact directory: {path}")
    console.rule("[bold cyan]QA Sentinel AI[/bold cyan]")

    if not run_analysis(path, console):
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
