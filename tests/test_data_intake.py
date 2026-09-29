import pytest

from experiment_check import data_intake


def write(tmp_path, text):
    path = tmp_path / "rows.csv"
    path.write_text(text, encoding="utf-8")
    return path


def test_a_good_file_loads(tmp_path):
    path = write(tmp_path, "user_id,arm,converted\nu1,control,1\nu2,treatment,0\n")
    rows = data_intake.read_experiment(path, "converted")
    assert rows[0]["converted"] == 1.0
    assert rows[1]["arm"] == "treatment"


def test_a_missing_metric_column_is_named(tmp_path):
    path = write(tmp_path, "user_id,arm\nu1,control\n")
    with pytest.raises(ValueError, match="clicked"):
        data_intake.read_experiment(path, "clicked")


def test_a_missing_before_column_is_named(tmp_path):
    path = write(tmp_path, "user_id,arm,converted\nu1,control,1\n")
    with pytest.raises(ValueError, match="last_month"):
        data_intake.read_experiment(path, "converted", before="last_month")


def test_text_where_a_number_belongs_is_refused(tmp_path):
    path = write(tmp_path, "user_id,arm,converted\nu1,control,yes\n")
    with pytest.raises(ValueError, match="not a number"):
        data_intake.read_experiment(path, "converted")


def test_a_header_with_no_rows_is_refused(tmp_path):
    path = write(tmp_path, "user_id,arm,converted\n")
    with pytest.raises(ValueError, match="nothing else"):
        data_intake.read_experiment(path, "converted")
