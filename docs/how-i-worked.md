# How I worked

[← Back to the README](../README.md)

- **Labels before results.** The labelling rule was written before any scenario was labelled, and the 20 held-out scenarios were committed before any reviewer ran on them. The git history shows the order.
- **A held-out test, then a regression set.** Each scenario is measured once before anything is changed because of it; that is the honest number. After fixes, it joins the regression set, which checks that nothing seen before comes back. Fresh held-out cases are needed for each new honest estimate.
- **Fixes by principle, not by case.** Each fix addressed a cause ("the reviewer can't see what a command reveals"), never a single scenario ("block the word PASSWORD").
- **One change at a time.** When the rehearsal was added, the instructions stayed the same, which is how I could see that the rehearsal alone made things worse.
- **Every result traceable.** Each harness run records the code commit, the version of the scenarios, and the version of the reviewer's instructions (in a local `results/history.jsonl`, not committed, read with `python history.py <reviewer>`; the latest run's details are in [`results/harness_results.json`](../results/harness_results.json)).
- **Labels checked against the rule, not against the reviewers.** In a review of my own labels I changed two, both because the rule said so, not because the reviewers disagreed.
