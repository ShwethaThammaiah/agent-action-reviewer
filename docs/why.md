# Why I built this

[← Back to the README](../README.md)

I lead engineering for a large-scale deployment platform, where one of the hardest problems is deciding automatically whether a change is causing harm and should be stopped. Working on it taught me three things I believe apply directly to AI agents.

**Stopping safe work has a real cost.** When our platform rolled back good changes, engineers lost days of progress, and they learned to retry past the safety system rather than trust it. Poor precision doesn't just waste time; it trains people to ignore the safeguard.

**Being cautious is not the same as being safe.** Even while rolling back far too often, harmful changes still got through. Noisy alerts got switched off, and incidents happened exactly where the checks had been silenced. Poor precision and poor recall happened at the same time.

**Good decisions need context, and good oversight needs a feedback loop.** What fixed our system was giving each decision the context it lacked, and having people review the automatic decisions so we could measure whether they were right.

AI agents now take actions on people's behalf: deleting files, sending data, running code. The same questions apply. How does a check tell harmful actions from safe ones? When should it interrupt a person, and what should it tell them? How do you know whether it's working? This project is a small-scale test of those ideas, and it reflects how I think about AI safety more broadly: safeguards should be measured, should explain themselves, and should keep a human meaningfully in charge without wearing them out.
