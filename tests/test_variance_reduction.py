import random

from experiment_check import variance_reduction


def rows_with_before(predictive, users=4000, seed=1):
    source = random.Random(seed)
    rows = []
    for user in range(users):
        before = source.gauss(0, 1)
        noise = source.gauss(0, 1)
        measured = before * predictive + noise
        rows.append(
            {"user_id": f"u{user}", "arm": "control", "spend": measured, "before": before}
        )
    return rows


def test_a_useless_before_period_changes_nothing():
    rows = rows_with_before(predictive=0.0)
    assert variance_reduction.spread_drop(rows, "spend", "before") < 0.01


def test_a_predictive_before_period_removes_most_of_the_noise():
    rows = rows_with_before(predictive=3.0)
    assert variance_reduction.spread_drop(rows, "spend", "before") > 0.80


def test_the_adjustment_keeps_every_row():
    rows = rows_with_before(predictive=1.0, users=100)
    assert len(variance_reduction.adjust_rows(rows, "spend", "before")) == 100


def test_a_flat_before_period_is_survived():
    rows = [
        {"user_id": "u1", "arm": "control", "spend": 1.0, "before": 2.0},
        {"user_id": "u2", "arm": "control", "spend": 3.0, "before": 2.0},
    ]
    assert variance_reduction.spread_drop(rows, "spend", "before") == 0.0
