# Resume project deep-dive track

This is a minimal adapter built on the common mastery protocol. Use it to test whether a learner can defend a resume claim or project credibly and technically.

## Inputs

Prefer the resume claim, target job description, and a GitHub repository fixed to a commit. If source evidence is unavailable, label claims as unverified instead of inventing implementation details.

## Dimensions

- problem, users, constraints, and success criteria;
- architecture and data flow;
- personal ownership versus team work;
- important implementation decisions and alternatives rejected;
- difficult bugs, failures, and recovery;
- performance, reliability, security, and observability;
- measured impact and how it was measured;
- what the learner would change now;
- consistency between the resume statement and repository evidence.

## Verification

Ask for a concise project explanation, then follow causal branches. Require repository-backed examples where possible. Use counterfactuals such as changed scale, failed dependency, tighter latency, data loss, abuse, or a different technology choice.

Do not optimize wording until the technical story and ownership claims are internally consistent. Save reusable technical Concepts globally; save project-specific evidence in the Target or Topic note.
