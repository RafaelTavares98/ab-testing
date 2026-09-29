"""Checks the checker.

Runs a thousand experiments where nothing was changed, and counts how
often the code claims a winner anyway. It must land near the alpha it
was given. Then it runs the same thousand while peeking, stopping at the
first green light, and counts again. The gap between the two numbers is
the reason this project exists.
"""

import sys

from data import make_experiment
from experiment_check import conversion_rate
from experiment_check import significance


ALPHA = 0.05
RUNS = 1000
USERS = 20000
BASELINE = 0.05
PEEKS = 10


def honest_error_rate(runs=RUNS, alpha=ALPHA):
    """One look, at the end, as the plan said."""
    claimed = 0
    for seed in range(runs):
        rows = make_experiment.make_rows(USERS, BASELINE, 0.0, seed)
        claimed += _p_value(rows) < alpha
    return claimed / runs


def peeking_error_rate(runs=RUNS, alpha=ALPHA, peeks=PEEKS):
    """Ten looks, stopping at the first green light."""
    claimed = 0
    for seed in range(runs):
        rows = make_experiment.make_rows(USERS, BASELINE, 0.0, seed)
        claimed += _stopped_early(rows, alpha, peeks)
    return claimed / runs


def _stopped_early(rows, alpha, peeks):
    for step in range(1, peeks + 1):
        so_far = rows[: len(rows) * step // peeks]
        if _p_value(so_far) < alpha:
            return True
    return False


def _p_value(rows):
    rates = conversion_rate.rates_by_arm(rows, "converted")
    return significance.two_proportion_p_value(rates)


def main():
    honest = honest_error_rate()
    peeking = peeking_error_rate()
    print(f"runs .................. {RUNS} A/A tests, {USERS} users each")
    print(f"alpha ................. {ALPHA}")
    print(f"one look at the end ... {honest:.1%} claimed a winner")
    print(f"peeking {PEEKS} times ...... {peeking:.1%} claimed a winner")
    return 0


if __name__ == "__main__":
    sys.exit(main())
