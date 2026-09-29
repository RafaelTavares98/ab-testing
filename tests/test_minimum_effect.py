import pytest

from experiment_check import minimum_effect


def rates(users, rate=0.05):
    arm = {"users": users, "conversions": users * rate, "rate": rate}
    return {"control": dict(arm), "treatment": dict(arm)}


def test_more_users_reveal_a_smaller_lift():
    small = minimum_effect.detectable_lift(rates(5000))
    large = minimum_effect.detectable_lift(rates(50000))
    assert large < small


def test_it_reproduces_the_hand_computed_sample_size():
    """5% baseline, 20% relative lift, 80% power, alpha 5%.

    The pooled formula, worked by hand, asks for about 7,460 users in
    each arm. Feed that back and the detectable lift must come out at
    20% again. If the two disagree, this file is wrong.
    """
    detectable = minimum_effect.detectable_lift(rates(7460, rate=0.05))
    assert detectable == pytest.approx(0.20, rel=0.02)


def test_a_baseline_that_is_not_a_rate_is_refused():
    broken = rates(1000)
    broken["control"]["rate"] = 0.0
    with pytest.raises(ValueError, match="not a conversion rate"):
        minimum_effect.detectable_lift(broken)
