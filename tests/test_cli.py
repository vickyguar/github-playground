import pandas as pd
from typer.testing import CliRunner

from argentina_data_lab.cli import app

runner = CliRunner()


def test_stats_command_prints_summary(tmp_path) -> None:
    input_file = tmp_path / "observations.csv"
    pd.DataFrame({"indice_tiempo": ["2024-01-01"], "value": [5]}).to_csv(
        input_file, index=False
    )

    result = runner.invoke(app, ["stats", str(input_file)])

    assert result.exit_code == 0, result.output
    assert '"mean": 5.0' in result.output


def test_stats_command_reports_missing_file(tmp_path) -> None:
    result = runner.invoke(app, ["stats", str(tmp_path / "missing.csv")])

    assert result.exit_code == 1
    assert "Error:" in result.output
