import pytest

from data import make_experiment


def test_same_seed_makes_the_same_rows():
    first = make_experiment.make_rows(500, 0.05, 0.1, seed=7)
    second = make_experiment.make_rows(500, 0.05, 0.1, seed=7)
    assert first == second


def test_no_lift_means_both_arms_share_a_rate():
    rows = make_experiment.make_rows(60000, 0.20, 0.0, seed=1)
    control = [row["converted"] for row in rows if row["arm"] == "control"]
    treatment = [row["converted"] for row in rows if row["arm"] == "treatment"]
    gap = abs(sum(control) / len(control) - sum(treatment) / len(treatment))
    assert gap < 0.01


def test_the_split_lands_near_the_half():
    rows = make_experiment.make_rows(20000, 0.05, 0.0, seed=3)
    treatment = sum(1 for row in rows if row["arm"] == "treatment")
    assert 0.48 < treatment / len(rows) < 0.52


def test_a_rate_above_one_is_refused():
    with pytest.raises(ValueError, match="passes 1"):
        make_experiment.make_rows(10, 0.9, 0.5, seed=1)


def test_the_broken_file_loses_part_of_one_arm():
    rows = make_experiment.make_rows(5000, 0.05, 0.0, seed=2)
    broken = make_experiment.break_split(rows)
    assert len(broken) < len(rows)


def test_writing_and_counting_the_file(tmp_path):
    rows = make_experiment.make_rows(50, 0.05, 0.0, seed=1)
    path = make_experiment.write_csv(rows, tmp_path / "rows.csv")
    assert path.read_text(encoding="utf-8").count("\n") == 51
