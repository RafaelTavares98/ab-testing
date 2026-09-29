"""Counts how many people did the thing, in each arm."""


def rates_by_arm(rows, metric):
    """Users, conversions and rate, for the control and the treatment."""
    summary = {}
    for arm in ("control", "treatment"):
        of_this_arm = [row for row in rows if row["arm"] == arm]
        summary[arm] = _one_arm(of_this_arm, metric, arm)
    return summary


def _one_arm(rows, metric, arm):
    users = len(rows)
    if users == 0:
        raise ValueError(f"the {arm} arm has no users, so it has no rate")
    conversions = sum(row[metric] for row in rows)
    return {
        "users": users,
        "conversions": conversions,
        "rate": conversions / users,
    }
