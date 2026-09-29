"""Asks whether the experiment was split the way it was planned.

When this fails, every other number in the test is measuring the break
and not the change.
"""

from collections import Counter

from scipy import stats


ALARM = 0.001


def check_split(rows, expected_share=0.5, alarm=ALARM):
    """The sample ratio mismatch test, plus the two dirt checks."""
    counts = Counter(row["arm"] for row in rows)
    _demand_two_arms(counts)
    control, treatment = counts["control"], counts["treatment"]
    p_value = _srm_p_value(control, treatment, expected_share)
    return {
        "control": control,
        "treatment": treatment,
        "expected_share": expected_share,
        "p_value": p_value,
        "passed": p_value >= alarm,
        "repeated_users": _repeated_users(rows),
        "crossed_users": _crossed_users(rows),
    }


def _srm_p_value(control, treatment, expected_share):
    total = control + treatment
    expected = [total * (1 - expected_share), total * expected_share]
    return float(stats.chisquare([control, treatment], expected).pvalue)


def _repeated_users(rows):
    seen = Counter(row["user_id"] for row in rows)
    return sorted(user for user, times in seen.items() if times > 1)


def _crossed_users(rows):
    arms_by_user = {}
    for row in rows:
        arms_by_user.setdefault(row["user_id"], set()).add(row["arm"])
    return sorted(user for user, arms in arms_by_user.items() if len(arms) > 1)


def _demand_two_arms(counts):
    missing = {"control", "treatment"} - set(counts)
    if missing:
        raise ValueError(f"the file has no rows in the {missing.pop()} arm")
