# argentina-data-lab

A Python 3.11+ command-line project for finding Argentine public statistical
series, downloading observations, summarizing data, and producing charts and
reports.

The client uses the official [Datos Argentina Series API](https://apis.datos.gob.ar/series/api)
and [Georef API](https://apis.datos.gob.ar/georef/api). Data and metadata are
provided by their respective Argentine public-sector publishers; cite the
original dataset when reusing results.

## Install

```bash
python -m pip install -e ".[dev]"
```

## Commands

Search series by keyword:

```bash
argentina-data-lab search "inflación" --limit 10
```

Download one or more series to CSV. IDs are the exact `field.id` values shown
by `search`:

```bash
argentina-data-lab fetch "SERIES_ID" --start-date 2020-01-01 --output data.csv
```

Calculate descriptive statistics, generate a chart, or export a JSON report
from a downloaded CSV:

```bash
argentina-data-lab stats data.csv
argentina-data-lab chart data.csv --output chart.png --title "Serie estadística"
argentina-data-lab report data.csv --output report.json
```

List Argentine provinces using Georef:

```bash
argentina-data-lab provinces
```

Run the tests with `python -m pytest`.
