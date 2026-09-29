"""The smallest lift this many people could ever have revealed.

Without it, "not significant" gets read as "no effect", and the two are
different sentences.
"""

import math

from scipy import stats


def detectable_lift(rates, alpha=0.05, power=0.8):
    """The relative lift this sample size would catch four times in five."""
    control, treatment = rates["control"], rates["treatment"]
    baseline = control["rate"]
    _demand_baseline(baseline)
    pull = stats.norm.ppf(1 - alpha / 2) + stats.norm.ppf(power)
    per_arm = _harmonic_users(control["users"], treatment["users"])
    absolute = pull * math.sqrt(2 * baseline * (1 - baseline) / per_arm)
    return absolute / baseline


def _harmonic_users(control_users, treatment_users):
    return 2 / (1 / control_users + 1 / treatment_users)


def _demand_baseline(baseline):
    if not 0 < baseline < 1:
        raise ValueError(f"a baseline of {baseline} is not a conversion rate")
