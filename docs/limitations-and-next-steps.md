# Limitations and next steps

[← Back to the README](../README.md)

## Limitations

- **Small and simple.** 60 scenarios, one person's labels, one reviewer model, a toy workspace of eight files. A small study, not a benchmark.
- **All 60 scenarios have now shaped the reviewer.** The held-out table is the honest estimate; a new held-out set would be needed for a fresh one.
- **URL calls are never actually sent.** A request leaves the sandbox by nature, so nothing could contain a wrong allow. The reviewer still judges every request; payments and messaging are represented only as URL calls.
- **The rehearsal can't cover actions that leave the sandbox,** such as a `git push`, and its credential check is a pattern match.
- **Rules are rigid by design.** Sharing data with a supplier at an address the agent chose is blocked even though asking would be fine. The rules' list of read-only commands is also short, which costs some unnecessary model calls.
- **Each model review is a network call.** It adds about two seconds, and sends the proposed action (not the rehearsal's credential values) to an external service.
- **The container can see some details of the host,** such as its disk size, though not its files.
- **No live feedback loop yet.** The labels measure the reviewer here; in real use, measuring it would need people to review its decisions.

## What I'd do next

- **Let people remember decisions, carefully.** "Always allow this exact action", never a pattern; never for anything touching secrets, leaving the workspace, or sending data out.
- **Show every block, and let people override the soft ones.** Each override is a free verdict that the block was wrong: the same signal on-call engineers gave by annotating automatic rollbacks, collected in the moment. Hard blocks stay fixed.
- **Treat a reviewer that disagrees with itself as unsure.** If two calls give different answers, ask the person rather than taking a vote.
- **Use filesystem snapshots instead of copies** for the rehearsal, so it scales beyond a small project.
- **Write fresh held-out scenarios regularly,** from real near-misses, and keep every old one as a regression test.
