"""Descriptive statistics for downloaded observations."""

from __future__ import annotations

import numpy as np
import pandas as pd


def describe_observations(frame: pd.DataFrame) -> dict[str, dict[str, float | int]]:
    """Calculate descriptive statistics for each numeric observation column."""
    numeric = frame.select_dtypes(include="number")
    if numeric.empty:
        raise ValueError("The input contains no numeric observation columns.")

    summary: dict[str, dict[str, float | int]] = {}
    for column in numeric:
        values = numeric[column].dropna().to_numpy(dtype=float)
        if values.size == 0:
            continue
        summary[str(column)] = {
            "count": int(values.size),
            "mean": float(np.mean(values)),
            "std": float(np.std(values, ddof=1)) if values.size > 1 else 0.0,
            "min": float(np.min(values)),
            "25%": float(np.percentile(values, 25)),
            "median": float(np.median(values)),
            "75%": float(np.percentile(values, 75)),
            "max": float(np.max(values)),
        }

    if not summary:
        raise ValueError("The input contains no non-empty numeric observations.")
    return summary
