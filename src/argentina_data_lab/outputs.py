"""Chart and report generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from argentina_data_lab.analysis import describe_observations


def create_chart(
    frame: pd.DataFrame,
    output: Path,
    *,
    title: str | None = None,
) -> None:
    """Plot numeric columns against the first column and save the chart."""
    numeric_columns = list(frame.select_dtypes(include="number").columns)
    if not numeric_columns:
        raise ValueError("The input contains no numeric observation columns.")
    if frame.empty:
        raise ValueError("The input contains no observations.")

    x_column = frame.columns[0]
    x_values = pd.to_datetime(frame[x_column], errors="coerce")
    if x_values.notna().any():
        x_values = x_values.where(x_values.notna(), frame[x_column])
    else:
        x_values = frame[x_column]

    figure, axis = plt.subplots(figsize=(10, 6))
    for column in numeric_columns:
        axis.plot(x_values, frame[column], label=str(column))
    axis.set_title(title or "Argentine public data")
    axis.set_xlabel(str(x_column))
    axis.set_ylabel("Value")
    axis.grid(True, alpha=0.3)
    if len(numeric_columns) > 1:
        axis.legend()
    figure.autofmt_xdate()
    figure.tight_layout()
    figure.savefig(output)
    plt.close(figure)


def export_report(frame: pd.DataFrame, output: Path) -> dict[str, Any]:
    """Write a JSON report with row count, date range, and series statistics."""
    if frame.empty:
        raise ValueError("The input contains no observations.")
    date_column = frame.columns[0]
    dates = pd.to_datetime(frame[date_column], errors="coerce").dropna()
    report: dict[str, Any] = {
        "source": "Argentina public data; see the original API dataset metadata.",
        "observations": int(len(frame)),
        "date_range": {
            "start": dates.min().strftime("%Y-%m-%d") if not dates.empty else None,
            "end": dates.max().strftime("%Y-%m-%d") if not dates.empty else None,
        },
        "statistics": describe_observations(frame),
    }
    output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return report
