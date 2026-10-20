import pandas as pd
import pytest

from argentina_data_lab.analysis import describe_observations


def test_describe_observations_calculates_summary() -> None:
    frame = pd.DataFrame({"value": [1, 2, 3, None]})

    result = describe_observations(frame)["value"]

    assert result == {
        "count": 3,
        "mean": 2.0,
        "std": 1.0,
        "min": 1.0,
        "25%": 1.5,
        "median": 2.0,
        "75%": 2.5,
        "max": 3.0,
    }


def test_describe_observations_rejects_non_numeric_input() -> None:
    with pytest.raises(ValueError, match="no numeric"):
        describe_observations(pd.DataFrame({"date": ["2024-01-01"]}))


def test_single_observation_has_zero_standard_deviation() -> None:
    result = describe_observations(pd.DataFrame({"value": [7]}))
    assert result["value"]["std"] == 0.0
