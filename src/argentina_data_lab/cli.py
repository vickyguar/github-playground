"""Command-line interface for argentina-data-lab."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import httpx
import pandas as pd
import typer

from argentina_data_lab.analysis import describe_observations
from argentina_data_lab.api import ArgentinaDataClient
from argentina_data_lab.outputs import create_chart, export_report

app = typer.Typer(
    name="argentina-data-lab",
    help="Explore official Argentine public statistics.",
    no_args_is_help=True,
)


def _run(action):
    try:
        return action()
    except (httpx.HTTPError, ValueError, OSError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc


@app.command()
def search(
    query: Annotated[str, typer.Argument(help="Keyword or phrase to search for.")],
    limit: Annotated[int, typer.Option(min=1, help="Maximum number of results.")] = 10,
) -> None:
    """Search statistical series in the Datos Argentina catalog."""

    def action() -> None:
        with ArgentinaDataClient() as client:
            result = client.search_series(query, limit=limit)
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))

    _run(action)


@app.command()
def fetch(
    ids: Annotated[str, typer.Argument(help="One or more series IDs, comma-separated.")],
    output: Annotated[Path, typer.Option(help="Destination CSV file.")],
    start_date: Annotated[str | None, typer.Option(help="First date, YYYY-MM-DD.")] = None,
    end_date: Annotated[str | None, typer.Option(help="Last date, YYYY-MM-DD.")] = None,
    limit: Annotated[int, typer.Option(min=1, help="Maximum observations.")] = 5000,
) -> None:
    """Download real observations from the Datos Argentina Series API."""

    def action() -> None:
        with ArgentinaDataClient() as client:
            frame = client.fetch_series(
                ids.split(","),
                start_date=start_date,
                end_date=end_date,
                limit=limit,
            )
        output.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(output, index=False)
        typer.echo(f"Saved {len(frame)} observations to {output}")

    _run(action)


@app.command()
def provinces() -> None:
    """List provinces from the Datos Argentina Georef API."""

    def action() -> None:
        with ArgentinaDataClient() as client:
            result = client.list_provinces()
        typer.echo(json.dumps(result, ensure_ascii=False, indent=2))

    _run(action)


@app.command()
def stats(
    input_file: Annotated[Path, typer.Argument(help="CSV file of observations.")],
) -> None:
    """Print descriptive statistics for a downloaded CSV."""

    def action() -> None:
        frame = pd.read_csv(input_file)
        typer.echo(json.dumps(describe_observations(frame), indent=2))

    _run(action)


@app.command()
def chart(
    input_file: Annotated[Path, typer.Argument(help="CSV file of observations.")],
    output: Annotated[Path, typer.Option(help="Destination image, e.g. chart.png.")],
    title: Annotated[str | None, typer.Option(help="Chart title.")] = None,
) -> None:
    """Generate a chart from a downloaded CSV."""

    def action() -> None:
        frame = pd.read_csv(input_file)
        output.parent.mkdir(parents=True, exist_ok=True)
        create_chart(frame, output, title=title)
        typer.echo(f"Saved chart to {output}")

    _run(action)


@app.command()
def report(
    input_file: Annotated[Path, typer.Argument(help="CSV file of observations.")],
    output: Annotated[Path, typer.Option(help="Destination JSON report.")],
) -> None:
    """Export a JSON report with date range and descriptive statistics."""

    def action() -> None:
        frame = pd.read_csv(input_file)
        output.parent.mkdir(parents=True, exist_ok=True)
        export_report(frame, output)
        typer.echo(f"Saved report to {output}")

    _run(action)
