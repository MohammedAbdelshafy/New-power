# New-power

This repository holds shared engineering rules and supporting scripts for Money Beast Machine. Jarvis uses it for reusable operating standards and capability registry material; product behavior belongs in the product's canonical repository.

## Where things live

- `MBM/Registry/`: shared capability and registry material.
- `scripts/`: small scripts for session setup, budget checks and updates.
- `templates/`: starter configuration and reusable templates.
- `.claude/` and `.github/`: tool/repository configuration and workflow automation.

## Working rules

- Check the current branch and file path before changing shared instructions.
- Make budget checks and credential handling easy to audit.
- Keep secrets in protected environment configuration, not in Git.
- Do not duplicate code owned by `jarvis-mbm`, `MBM-Control`, or `MBM-Social`.
- When a change affects shared behavior, document the consumer and how it is checked.

## Portfolio routing

The current portfolio map lives in [Jarvis ICM](https://github.com/MohammedAbdelshafy/jarvis-mbm/blob/feature/icm-portfolio-map/ICM/REPO_MAP.md). The root documentation here is an entry point, not a replacement for the live registry or product-specific contract.
