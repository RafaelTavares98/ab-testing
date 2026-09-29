import pytest

from data import make_experiment
from experiment_check import confidence_interval
from experiment_check import conversion_rate


def rates_of(users, control_rate, lift, seed):
    rows = make_experiment.make_rows(users, control_rate, lift, seed)
    return conversion_rate.rates_by_arm(rows, "converted")


def test_the_interval_holds_the_true_lift():
    interval = confidence_interval.lift_interval(rates_of(40000, 0.10, 0.15, 11))
    assert interval["low"] < 0.15 < interval["high"]


def test_the_interval_is_the_stated_width_in_the_long_run():
    """Two hundred experiments, and about ten of them should miss."""
    caught = 0
    for seed in range(200):
        interval = confidence_interval.lift_interval(
            rates_of(8000, 0.20, 0.10, seed)
        )
        caught += interval["low"] < 0.10 < interval["high"]
    assert 0.90 <= caught / 200 <= 0.99


def test_an_arm_that_converted_nobody_is_refused():
    empty = {
        "control": {"users": 100, "conversions": 0, "rate": 0.0},
        "treatment": {"users": 100, "conversions": 5, "rate": 0.05},
    }
    with pytest.raises(ValueError, match="no ratio"):
        confidence_interval.lift_interval(empty)
