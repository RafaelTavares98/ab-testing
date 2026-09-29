from data import make_experiment
from experiment_check import analysis
from experiment_check import report


def rows(lift=0.15, users=30000, seed=9):
    return make_experiment.make_rows(users, 0.05, lift, seed)


def test_a_healthy_test_prints_every_line():
    printed = report.render(analysis.analyse(rows(), "converted"))
    for label in ("SRM check", "Users", "Conversion", "Lift", "Verdict"):
        assert label in printed


def test_a_broken_split_prints_the_refusal_and_no_numbers():
    broken = make_experiment.break_split(rows(lift=0.0, users=30000))
    printed = report.render(analysis.analyse(broken, "converted"))
    assert "FAIL" in printed
    assert "Do not read this test." in printed
    assert "Conversion" not in printed


def test_the_cuped_line_only_appears_when_asked():
    result = analysis.analyse(rows(), "converted", before="before")
    assert "CUPED" in report.render(result)
    assert "CUPED" not in report.render(analysis.analyse(rows(), "converted"))
