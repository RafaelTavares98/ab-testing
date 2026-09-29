"""Invents an experiment whose true answer is known in advance.

Nothing else in this project can be trusted until this exists. A checker
with no known answer to check against proves nothing.
"""

import csv
import math
import random


COLUMNS = ["user_id", "arm", "converted", "before"]


def make_rows(users, control_rate, lift, seed, split=0.5):
    """One row per user, with the true lift built into the treatment arm.

    `lift` is relative: 0.10 means the treatment converts 10 per cent
    more often than the control.
    """
    _reject_bad_rates(control_rate, lift, split)
    source = random.Random(seed)
    rows = []
    for user in range(users):
        arm = "treatment" if source.random() < split else "control"
        habit = _habit(source, control_rate)
        rate = habit * (1 + lift) if arm == "treatment" else habit
        before = _before_period(source, habit)
        converted = 1 if source.random() < min(rate, 0.999) else 0
        rows.append(
            {
                "user_id": f"u{user}",
                "arm": arm,
                "converted": converted,
                "before": round(before, 6),
            }
        )
    return rows


def break_split(rows, keep_treatment=0.90):
    """Drops part of one arm, the way a broken redirect drops it."""
    source = random.Random(0)
    kept = []
    for row in rows:
        if row["arm"] == "treatment" and source.random() > keep_treatment:
            continue
        kept.append(row)
    return kept


def duplicate_user(rows):
    """Repeats one user, the way a double-fired event repeats one."""
    return rows + [dict(rows[0])]


def cross_assign_user(rows):
    """Puts one user in both arms, the way a lost cookie does."""
    crossed = dict(rows[0])
    crossed["arm"] = _other_arm(rows[0]["arm"])
    return rows + [crossed]


def write_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def _habit(source, control_rate):
    """Each person carries their own habit, not the crowd's average.

    Without this the before period predicts nothing, and CUPED has no
    noise to remove, which is not what real data looks like.
    """
    return min(control_rate * math.exp(source.gauss(0, 0.6)), 0.9)


def _before_period(source, habit, trials=20):
    """What this person did over twenty chances before the test."""
    hits = sum(1 for _ in range(trials) if source.random() < habit)
    return hits / trials


def _other_arm(arm):
    return "control" if arm == "treatment" else "treatment"


def _reject_bad_rates(control_rate, lift, split):
    if not 0 < control_rate < 1:
        raise ValueError(f"control_rate must sit between 0 and 1, got {control_rate}")
    if control_rate * (1 + lift) >= 1:
        raise ValueError("control_rate times the lift passes 1, which is not a rate")
    if not 0 < split < 1:
        raise ValueError(f"split must sit between 0 and 1, got {split}")
