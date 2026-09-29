import pytest

from data import make_experiment
from experiment_check import split_health


def test_a_clean_split_passes():
    rows = make_experiment.make_rows(20000, 0.05, 0.0, seed=5)
    assert split_health.check_split(rows)["passed"]


def test_a_broken_split_fails_and_says_how_sure():
    rows = make_experiment.make_rows(20000, 0.05, 0.0, seed=5)
    broken = make_experiment.break_split(rows, keep_treatment=0.94)
    checked = split_health.check_split(broken)
    assert not checked["passed"]
    assert checked["p_value"] < 0.001


def test_a_small_sample_does_not_raise_the_alarm():
    rows = [{"user_id": f"u{n}", "arm": "control"} for n in range(52)]
    rows += [{"user_id": f"t{n}", "arm": "treatment"} for n in range(48)]
    assert split_health.check_split(rows)["passed"]


def test_a_repeated_user_is_named():
    rows = make_experiment.make_rows(2000, 0.05, 0.0, seed=1)
    checked = split_health.check_split(make_experiment.duplicate_user(rows))
    assert checked["repeated_users"] == ["u0"]


def test_a_user_in_both_arms_is_named():
    rows = make_experiment.make_rows(2000, 0.05, 0.0, seed=1)
    checked = split_health.check_split(make_experiment.cross_assign_user(rows))
    assert checked["crossed_users"] == ["u0"]


def test_one_arm_alone_is_refused():
    rows = [{"user_id": "u1", "arm": "control"}]
    with pytest.raises(ValueError, match="no rows in the treatment arm"):
        split_health.check_split(rows)
