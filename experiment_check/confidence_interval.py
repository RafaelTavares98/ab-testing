"""The range the true lift probably sits in.

A point estimate on its own invites someone to ship a coin flip. The
interval is what makes the decision honest.
"""

import math

from scipy import stats


def lift_interval(rates, alpha=0.05):
    """Relative lift and its interval, on the log ratio of two rates."""
    control, treatment = rates["control"], rates["treatment"]
    _demand_movement(control, treatment)
    ratio = treatment["rate"] / control["rate"]
    spread = _log_standard_error(control, treatment)
    edge = stats.norm.ppf(1 - alpha / 2) * spread
    return {
        "lift": ratio - 1,
        "low": math.exp(math.log(ratio) - edge) - 1,
        "high": math.exp(math.log(ratio) + edge) - 1,
        "alpha": alpha,
    }


def _log_standard_error(control, treatment):
    return math.sqrt(
        _one_arm_term(control) + _one_arm_term(treatment)
    )


def _one_arm_term(arm):
    return (1 - arm["rate"]) / (arm["rate"] * arm["users"])


def _demand_movement(control, treatment):
    if control["rate"] == 0 or treatment["rate"] == 0:
        raise ValueError("an arm converted nobody, so there is no ratio to read")
