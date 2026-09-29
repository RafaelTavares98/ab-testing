import pytest
from scipy import stats

from experiment_check import significance


def rates(control, control_users, treatment, treatment_users):
    return {
        "control": {
            "users": control_users,
            "conversions": control,
            "rate": control / control_users,
        },
        "treatment": {
            "users": treatment_users,
            "conversions": treatment,
            "rate": treatment / treatment_users,
        },
    }


def test_identical_arms_give_a_p_value_of_one():
    same = rates(500, 10000, 500, 10000)
    assert significance.two_proportion_p_value(same) == pytest.approx(1.0)


def test_an_obvious_difference_gives_a_p_value_near_zero():
    obvious = rates(200, 10000, 900, 10000)
    assert significance.two_proportion_p_value(obvious) < 1e-10


def test_the_result_matches_the_chi_square_on_the_same_table():
    """The pooled z test and the uncorrected chi-square are the same test.

    Two roads to one number. If ours disagrees, ours is wrong.
    """
    ours = rates(481, 10000, 544, 10000)
    table = [[481, 10000 - 481], [544, 10000 - 544]]
    theirs = stats.chi2_contingency(table, correction=False).pvalue
    assert significance.two_proportion_p_value(ours) == pytest.approx(theirs, abs=1e-5)
