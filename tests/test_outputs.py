import json

import pandas as pd

from argentina_data_lab.outputs import create_chart, export_report


def test_export_report_writes_statistics_and_date_range(tmp_path) -> None:
    output = tmp_path / "report.json"
    frame = pd.DataFrame(
        {"indice_tiempo": ["2024-01-01", "2024-02-01"], "value": [10, 20]}
    )

    report = export_report(frame, output)

    saved = json.loads(output.read_text(encoding="utf-8"))
    assert report == saved
    assert saved["observations"] == 2
    assert saved["date_range"] == {"start": "2024-01-01", "end": "2024-02-01"}
    assert saved["statistics"]["value"]["mean"] == 15


def test_create_chart_saves_image(tmp_path) -> None:
    output = tmp_path / "chart.png"
    frame = pd.DataFrame(
        {"indice_tiempo": ["2024-01-01", "2024-02-01"], "value": [10, 20]}
    )

    create_chart(frame, output, title="Inflación")

    assert output.is_file()
    assert output.stat().st_size > 0
