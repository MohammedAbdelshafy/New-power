---
type: repository
status: active
owner_repo: MohammedAbdelshafy/New-power
source_of_truth: https://github.com/MohammedAbdelshafy/New-power
---

# MBM Engineering OS CONTEXT

One job: hold shared engineering policies, registry material and scripts that multiple MBM workflows rely on.

## Inputs
- Overview: [README](README.md)
- Shared capability records: [MBM/Registry](MBM/Registry/)
- Scripts: [scripts](scripts/)
- Templates: [templates](templates/)
- Portfolio routing: [Jarvis ICM map](https://github.com/MohammedAbdelshafy/jarvis-mbm/blob/feature/icm-portfolio-map/ICM/CONTEXT.md)

## Process
1. Identify which downstream repo/script consumes the material.
2. Inspect the current branch and its existing instructions.
3. Keep shared policy separate from product implementation.
4. Test script behavior on safe sample inputs.
5. Record how the change can be reversed.

## Output
Reviewed shared standards, capability records, scripts or templates.

## Check
No secret values in Git. No duplicated product implementation. A change is complete only when its actual consumer and verification method are named.
