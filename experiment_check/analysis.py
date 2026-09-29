"""Runs the checks in the one order that makes sense.

Health first, always. A number computed on a broken split is worse than
no number, because someone will act on it.
"""

from experiment_check import confidence_interval
from experiment_check import conversion_rate
from experiment_check import minimum_effect
from experiment_check import significance
from experiment_check import split_health
from experiment_check import variance_reduction
from experiment_check import verdict


def analyse(rows, metric, alpha=0.05, expected_share=0.5, before=None):
    health = split_health.check_split(rows, expected_share)
    if not health["passed"]:
        return _refusal(health, alpha)
    rates = conversion_rate.rates_by_arm(rows, metric)
    interval = confidence_interval.lift_interval(rates, alpha)
    p_value = significance.two_proportion_p_value(rates)
    detectable = minimum_effect.detectable_lift(rates, alpha)
    return {
        "health": health,
        "rates": rates,
        "interval": interval,
        "p_value": p_value,
        "detectable": detectable,
        "spread_drop": _spread_drop(rows, metric, before),
        "verdict": verdict.decide(health, interval, p_value, detectable, alpha),
    }


def _refusal(health, alpha):
    return {
        "health": health,
        "rates": None,
        "interval": {"alpha": alpha},
        "p_value": None,
        "detectable": None,
        "spread_drop": None,
        "verdict": verdict.decide(health, None, None, None, alpha),
    }


def _spread_drop(rows, metric, before):
    if not before:
        return None
    return variance_reduction.spread_drop(rows, metric, before)
