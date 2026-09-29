"""CUPED: cancels the noise each user brought with them.

A user who already converted often before the test is not evidence that
the new button works. Subtracting what they were always going to do
leaves a narrower, honest interval.
"""

import statistics


def adjust_rows(rows, metric, before):
    """Returns the rows with the metric corrected by the before period."""
    theta = _theta(rows, metric, before)
    before_mean = statistics.fmean(row[before] for row in rows)
    adjusted = []
    for row in rows:
        corrected = dict(row)
        corrected[metric] = row[metric] - theta * (row[before] - before_mean)
        adjusted.append(corrected)
    return adjusted


def spread_drop(rows, metric, before):
    """How much of the noise the before period removes, as a fraction."""
    raw = statistics.variance([row[metric] for row in rows])
    if raw == 0:
        return 0.0
    adjusted = adjust_rows(rows, metric, before)
    left = statistics.variance([row[metric] for row in adjusted])
    return 1 - left / raw


def _theta(rows, metric, before):
    before_values = [row[before] for row in rows]
    spread = statistics.variance(before_values)
    if spread == 0:
        return 0.0
    metric_values = [row[metric] for row in rows]
    return statistics.covariance(metric_values, before_values) / spread
