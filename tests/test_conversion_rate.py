import pytest

from experiment_check import conversion_rate


TEN_ROWS = (
    [{"user_id": f"c{n}", "arm": "control", "converted": 1} for n in range(2)]
    + [{"user_id": f"c{n}", "arm": "control", "converted": 0} for n in range(3)]
    + [{"user_id": f"t{n}", "arm": "treatment", "converted": 1} for n in range(3)]
    + [{"user_id": f"t{n}", "arm": "treatment", "converted": 0} for n in range(2)]
)


def test_counts_and_rates_match_the_hand_count():
    rates = conversion_rate.rates_by_arm(TEN_ROWS, "converted")
    assert rates["control"] == {"users": 5, "conversions": 2, "rate": 0.4}
    assert rates["treatment"] == {"users": 5, "conversions": 3, "rate": 0.6}


def test_an_empty_arm_is_refused_instead_of_dividing_by_zero():
    only_control = [row for row in TEN_ROWS if row["arm"] == "control"]
    with pytest.raises(ValueError, match="no users"):
        conversion_rate.rates_by_arm(only_control, "converted")
