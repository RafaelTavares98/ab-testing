# experiment-check

Reads an A/B test and tells you whether you are allowed to read it.

Most tools hand you a p-value. This one checks first whether the
experiment was set up correctly, and refuses to print a single number
when it was not. A result computed on a broken split is worse than no
result, because somebody will act on it.

```
experiment-check run results.csv --metric converted
```

## What it prints

A test that is sound:

```
SRM check ............. pass  50.0% / 50.0% expected 50% / 50%, p = 0.8265
Users ................. 39,969 control, 40,031 treatment
Conversion ............ 5.94% control, 6.98% treatment
Lift .................. +17.5%  [+11.5%, +23.9%] at 95%
Significant ........... yes, p = 0.000
Detectable effect ..... this test could see +7.9% or larger
CUPED ................. the before period removes 1.2% of the noise
Verdict ............... Ship it.
Reason ................ The gain is real, and the worst case in the interval is still positive.
```

A test whose split is broken. Nothing else is printed, on purpose:

```
SRM check ............. FAIL  52.6% / 47.4% expected 50% / 50%, p = 0.0000
Verdict ............... Do not read this test.
Reason ................ The split is broken, so every number below it would be measuring the break and not the change.
```

A test that simply did not have enough people:

```
Lift .................. +11.8%  [-4.9%, +31.4%] at 95%
Significant ........... no, p = 0.176
Detectable effect ..... this test could see +23.7% or larger
Verdict ............... The test was too small to answer.
Reason ................ This many users could only reveal a lift of 23.7% or larger. Nothing was proved either way.
```

That last verdict matters. "Not significant" gets read as "no effect"
every day of the week, and they are different sentences. The first means
we learned nothing. The second means we learned something.

## Why the split check comes first

You planned a 50/50 split and got 52.6/47.4. With 80,000 users that gap
cannot happen by chance. It means the assignment itself is broken: a
redirect that drops people, a trigger that fires late, events that never
arrive. Microsoft's experiment team calls this a fever: one symptom with
many possible illnesses. Whatever the illness, the arms are no longer
comparable, so the conversion rates are measuring the break rather than
the change you made.

The check is a chi-square test against the planned share, with the alarm
set at p < 0.001. That threshold is deliberate: at p < 0.05 the alarm
would cry wolf on one healthy experiment in twenty.

It also names any user counted twice, and any user found in both arms.
Either one makes the arms dependent, and the same refusal applies.

## Does the checker actually work

The repository ships the proof, not a promise. `data/calibrate.py` runs
1,000 experiments in which **nothing was changed at all**, and counts how
often the code claims a winner anyway. At an alpha of 5%, the honest
answer is about 5%.

```
runs .................. 1000 A/A tests, 20000 users each
alpha ................. 0.05
one look at the end ... 4.7% claimed a winner
peeking 10 times ...... 19.1% claimed a winner
```

The second line is the argument for the whole project. Same data, same
code, same alpha. The only difference is that the second run looked at
the test ten times and stopped the moment it went green. Peeking turned
a 1-in-20 error rate into a 1-in-5 error rate.

Run it yourself:

```
python -m data.calibrate
```

It takes about four minutes.

## What it does

| Check | What it answers |
| --- | --- |
| Sample ratio mismatch | Was the experiment split the way it was planned? |
| Repeated and crossed users | Is each person counted once, in one arm? |
| Conversion rates | How many people in each arm did the thing? |
| Two-proportion test | Could this gap be luck? |
| Confidence interval | How big is the effect, and how sure are we? |
| Minimum detectable effect | Was this test ever big enough to answer? |
| CUPED | How much noise does the before period remove? |
| Verdict | One sentence a person can act on. |

## About the CUPED line

CUPED subtracts what each user was always going to do, using their
behaviour from before the test, and leaves a narrower interval for the
same number of users.

On the binary conversion metric in the example it removes about 1% of
the noise, which is close to nothing. On a continuous metric with a
predictive history, such as revenue per user, the same code removes more
than 80% of it. That case is in `tests/test_variance_reduction.py`. The
line is printed rather than hidden because a method that helped a little
should be reported as having helped a little.

## Installing and running

```
pip install -r requirements.txt
python -m data.make_files
python -m experiment_check.cli data/healthy.csv --metric converted --before before
python -m experiment_check.cli data/broken_split.csv --metric converted
```

The first command writes the three example files from fixed seeds, so
they come back identical and reproduce every block above. They are not
committed: eighty thousand rows belong in a command, not in a
repository.

The input is one CSV row per user:

```
user_id,arm,converted,before
u0,control,0,0.05
u1,treatment,1,0.10
```

`arm` holds `control` or `treatment`. `--metric` names the measured
column. `--before` is optional and turns on the CUPED line. The exit
code is 0 when the test can be read and 1 when it cannot, so it fits in
a pipeline.

## The tests

```
python -m pytest
```

44 tests. None of them opens a socket, a database or a file it did not
write itself. The interesting ones:

* The two-proportion test is checked against `scipy`'s chi-square on the
  same table. They are the same test by two roads, so a disagreement
  means this code is wrong.
* The 95% interval is checked by running 200 generated experiments with
  a known lift and counting how often the interval contains it. It has
  to land near 95%, and it does.
* The split alarm is checked in both directions: it must fire on a 52/48
  split with 30,000 users, and it must stay quiet on a 52/48 split with
  100 users, where that gap is ordinary.
* The minimum detectable effect is checked against the sample size
  worked by hand from the pooled formula.

## What this is not

It is not a feature-flag service, an assignment service, or a dashboard.
It does not run your experiment. It reads a file after the fact and
gives one verdict.

It handles one metric, two arms, and a fixed-horizon test. It does not
do sequential testing, so it cannot make peeking safe. It only measures
how badly peeking goes wrong, which is why the calibration run is the
first thing in this readme after the output.

## The data

`data/make_experiment.py` invents experiments whose true lift is known,
so every claim above can be checked rather than believed. Each user
carries their own habit, so the before period actually predicts
something, the way it does in real data. It can also break a file on
purpose: drop part of one arm, repeat a user, or put a user in both
arms. `data/make_files.py` writes the three examples used above.

Nothing in this repository is a client's data.
