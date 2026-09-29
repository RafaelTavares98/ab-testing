"""Prints the block a person reads in five seconds."""


def render(result):
    """The full report, or the refusal on its own when the split broke."""
    lines = [_health_line(result["health"])]
    if result["verdict"]["verdict"] == "Do not read this test.":
        lines += _closing(result)
        return "\n".join(lines)
    lines += _numbers(result)
    lines += _closing(result)
    return "\n".join(lines)


def _health_line(health):
    total = health["control"] + health["treatment"]
    share = health["treatment"] / total
    state = "pass" if health["passed"] else "FAIL"
    return _row(
        "SRM check",
        f"{state}  {1 - share:.1%} / {share:.1%} "
        f"expected {1 - health['expected_share']:.0%} / "
        f"{health['expected_share']:.0%}, p = {health['p_value']:.4f}",
    )


def _numbers(result):
    rates, interval = result["rates"], result["interval"]
    lines = [
        _row(
            "Users",
            f"{rates['control']['users']:,} control, "
            f"{rates['treatment']['users']:,} treatment",
        ),
        _row(
            "Conversion",
            f"{rates['control']['rate']:.2%} control, "
            f"{rates['treatment']['rate']:.2%} treatment",
        ),
        _row(
            "Lift",
            f"{interval['lift']:+.1%}  [{interval['low']:+.1%}, "
            f"{interval['high']:+.1%}] at {1 - interval['alpha']:.0%}",
        ),
        _row("Significant", _significance_words(result)),
        _row(
            "Detectable effect",
            f"this test could see {result['detectable']:+.1%} or larger",
        ),
    ]
    if result.get("spread_drop") is not None:
        lines.append(
            _row(
                "CUPED",
                f"the before period removes {result['spread_drop']:.1%} of the noise",
            )
        )
    return lines


def _closing(result):
    return [
        _row("Verdict", result["verdict"]["verdict"]),
        _row("Reason", result["verdict"]["reason"]),
    ]


def _significance_words(result):
    alpha = result["interval"]["alpha"]
    word = "yes" if result["p_value"] < alpha else "no"
    return f"{word}, p = {result['p_value']:.3f}"


def _row(label, value):
    return f"{label} {'.' * max(1, 22 - len(label))} {value}"
