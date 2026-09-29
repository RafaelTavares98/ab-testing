import pytest

from data import make_experiment
from experiment_check import cli


def written(tmp_path, rows):
    return str(make_experiment.write_csv(rows, tmp_path / "rows.csv"))


def test_a_healthy_file_prints_a_verdict_and_returns_zero(tmp_path, capsys):
    rows = make_experiment.make_rows(30000, 0.05, 0.15, seed=9)
    code = cli.main([written(tmp_path, rows), "--metric", "converted"])
    assert code == 0
    assert "Verdict" in capsys.readouterr().out


def test_a_broken_file_returns_one(tmp_path, capsys):
    rows = make_experiment.break_split(
        make_experiment.make_rows(30000, 0.05, 0.0, seed=9)
    )
    code = cli.main([written(tmp_path, rows), "--metric", "converted"])
    assert code == 1
    assert "Do not read this test." in capsys.readouterr().out


def test_a_missing_column_stops_the_run(tmp_path):
    rows = make_experiment.make_rows(100, 0.05, 0.0, seed=1)
    with pytest.raises(ValueError, match="clicked"):
        cli.main([written(tmp_path, rows), "--metric", "clicked"])
