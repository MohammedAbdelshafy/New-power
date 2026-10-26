---
type: repository
status: active
owner_repo: MohammedAbdelshafy/New-power
product_name: MBM Engineering OS
source_of_truth: https://github.com/MohammedAbdelshafy/New-power
---

# MBM Engineering OS CONTEXT

One job: hold shared engineering rules, capability records and reusable tools used by the MBM portfolio.

## Inputs
- Registry: [MBM/Registry](MBM/Registry/)
- Setup: [install.sh](install.sh)
- Scripts: [scripts](scripts/)
- Templates: [templates](templates/)
- Portfolio routing: [Jarvis ICM](https://github.com/MohammedAbdelshafy/jarvis-mbm/blob/feature/icm-portfolio-map/ICM/CONTEXT.md)

## Process
1. Identify whether a change is truly shared or belongs to a product repo.
2. Inspect the current source, registry and dependencies before altering a shared capability.
3. Record license/security checks and only then pin or enable third-party tooling.
4. Preserve governance gates and avoid creating a second owner for an existing subsystem.
5. Link to product implementations instead of copying their source.

## Output
Shared rules, capability metadata, setup scripts and reusable templates.

## Check
A change has a clear owner, source, intended consumer and fallback. No production behavior changes merely because documentation or a tool was added to the registry.
