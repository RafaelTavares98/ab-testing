"""Reads the experiment file and complains about what is missing."""

import csv


REQUIRED = ["user_id", "arm"]


def read_experiment(path, metric, before=None):
    """Rows as dictionaries, with the metric already a number."""
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"{path} holds a header and nothing else")
    _demand_columns(rows[0], metric, before)
    return [_convert_row(row, metric, before) for row in rows]


def _demand_columns(first_row, metric, before):
    wanted = REQUIRED + [metric] + ([before] if before else [])
    missing = [name for name in wanted if name not in first_row]
    if missing:
        raise ValueError(f"the file has no column called {', '.join(missing)}")


def _convert_row(row, metric, before):
    converted = dict(row)
    converted[metric] = _as_number(row[metric], metric)
    if before:
        converted[before] = _as_number(row[before], before)
    return converted


def _as_number(value, column):
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"column {column} holds {value!r}, which is not a number")
