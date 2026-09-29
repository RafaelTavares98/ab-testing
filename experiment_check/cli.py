"""The only file that reads the command line."""

import argparse
import sys

from experiment_check import analysis
from experiment_check import data_intake
from experiment_check import report


def main(argv=None):
    options = _read_options(argv)
    rows = data_intake.read_experiment(
        options.path, options.metric, options.before
    )
    result = analysis.analyse(
        rows,
        options.metric,
        alpha=options.alpha,
        expected_share=options.expected_share,
        before=options.before,
    )
    print(report.render(result))
    return 0 if result["health"]["passed"] else 1


def _read_options(argv):
    parser = argparse.ArgumentParser(
        prog="experiment-check",
        description="Says whether an A/B test can be read, and what it says.",
    )
    parser.add_argument("path", help="the CSV with one row per user")
    parser.add_argument("--metric", required=True, help="the column that was measured")
    parser.add_argument("--before", help="a column from before the test, for CUPED")
    parser.add_argument("--alpha", type=float, default=0.05)
    parser.add_argument("--expected-share", type=float, default=0.5)
    return parser.parse_args(argv)


if __name__ == "__main__":
    sys.exit(main())
