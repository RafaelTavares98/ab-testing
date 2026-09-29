"""Turns the numbers into the sentence a person has to act on."""


DO_NOT_READ = "Do not read this test."
SHIP = "Ship it."
KEEP = "Keep the control."
TOO_SMALL = "The test was too small to answer."


def decide(health, interval, p_value, detectable, alpha=0.05):
    """One verdict, and the reason for it, in that order of authority."""
    if not health["passed"]:
        return _broken_split(health)
    if health["crossed_users"] or health["repeated_users"]:
        return _dirty_rows(health)
    if p_value < alpha:
        return _significant(interval)
    return _not_significant(interval, detectable)


def _broken_split(health):
    return {
        "verdict": DO_NOT_READ,
        "reason": (
            "The split is broken, so every number below it would be "
            "measuring the break and not the change."
        ),
    }


def _dirty_rows(health):
    counted = len(health["crossed_users"]) + len(health["repeated_users"])
    return {
        "verdict": DO_NOT_READ,
        "reason": (
            f"{counted} user or users are counted twice, or sit in both "
            "arms, so the arms are not independent."
        ),
    }


def _significant(interval):
    if interval["low"] > 0:
        return {
            "verdict": SHIP,
            "reason": (
                "The gain is real, and the worst case in the interval is "
                "still positive."
            ),
        }
    if interval["high"] < 0:
        return {
            "verdict": KEEP,
            "reason": "The change loses, and the best case in the interval still loses.",
        }
    return {
        "verdict": TOO_SMALL,
        "reason": "The test is significant but the interval crosses zero, which is a contradiction worth investigating.",
    }


def _not_significant(interval, detectable):
    if abs(interval["lift"]) < detectable:
        return {
            "verdict": TOO_SMALL,
            "reason": (
                f"This many users could only reveal a lift of "
                f"{detectable:.1%} or larger. Nothing was proved either way."
            ),
        }
    return {
        "verdict": KEEP,
        "reason": "The test had the size to find a change this large and did not find one.",
    }
