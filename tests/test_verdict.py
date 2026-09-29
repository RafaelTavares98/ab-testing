from experiment_check import verdict


def health(passed=True, repeated=None, crossed=None):
    return {
        "control": 1000,
        "treatment": 1000,
        "expected_share": 0.5,
        "p_value": 0.5 if passed else 0.0001,
        "passed": passed,
        "repeated_users": repeated or [],
        "crossed_users": crossed or [],
    }


def interval(lift, low, high):
    return {"lift": lift, "low": low, "high": high, "alpha": 0.05}


def test_a_broken_split_beats_a_beautiful_p_value():
    decided = verdict.decide(
        health(passed=False), interval(0.30, 0.20, 0.40), 0.0001, 0.05
    )
    assert decided["verdict"] == verdict.DO_NOT_READ


def test_a_repeated_user_stops_the_reading_too():
    decided = verdict.decide(
        health(repeated=["u1"]), interval(0.30, 0.20, 0.40), 0.0001, 0.05
    )
    assert decided["verdict"] == verdict.DO_NOT_READ


def test_a_real_gain_says_ship():
    decided = verdict.decide(health(), interval(0.13, 0.02, 0.25), 0.01, 0.05)
    assert decided["verdict"] == verdict.SHIP


def test_a_real_loss_says_keep_the_control():
    decided = verdict.decide(health(), interval(-0.13, -0.25, -0.02), 0.01, 0.05)
    assert decided["verdict"] == verdict.KEEP


def test_a_small_test_is_not_called_no_effect():
    decided = verdict.decide(health(), interval(0.03, -0.20, 0.28), 0.6, 0.25)
    assert decided["verdict"] == verdict.TOO_SMALL
    assert "either way" in decided["reason"]


def test_a_big_test_that_found_nothing_says_keep_the_control():
    decided = verdict.decide(health(), interval(0.01, -0.02, 0.04), 0.6, 0.005)
    assert decided["verdict"] == verdict.KEEP
