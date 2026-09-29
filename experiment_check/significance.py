"""Answers one question: could this gap be luck?"""

import math

from scipy import stats


def two_proportion_p_value(rates):
    """The pooled two-sided z test on two conversion rates."""
    control, treatment = rates["control"], rates["treatment"]
    pooled = _pooled_rate(control, treatment)
    spread = _standard_error(pooled, control["users"], treatment["users"])
    if spread == 0:
        return 1.0
    z = (treatment["rate"] - control["rate"]) / spread
    return float(2 * (1 - stats.norm.cdf(abs(z))))


def _pooled_rate(control, treatment):
    conversions = control["conversions"] + treatment["conversions"]
    users = control["users"] + treatment["users"]
    return conversions / users


def _standard_error(pooled, control_users, treatment_users):
    variance = pooled * (1 - pooled)
    return math.sqrt(variance * (1 / control_users + 1 / treatment_users))
