"""Writes the three example files the readme talks about.

They are not committed, because a CSV of eighty thousand rows belongs in
a command and not in a repository. Every seed here is fixed, so the
files come back byte for byte identical.
"""

import sys

from data import make_experiment


def main():
    healthy = make_experiment.make_rows(80000, 0.05, 0.15, seed=42)
    make_experiment.write_csv(healthy, "data/healthy.csv")
    make_experiment.write_csv(
        make_experiment.break_split(healthy), "data/broken_split.csv"
    )
    make_experiment.write_csv(
        make_experiment.make_rows(9000, 0.05, 0.08, seed=7), "data/too_small.csv"
    )
    print("wrote data/healthy.csv, data/broken_split.csv, data/too_small.csv")
    return 0


if __name__ == "__main__":
    sys.exit(main())
