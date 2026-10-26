# MBM Engineering OS

This repository holds shared rules and reusable operating pieces for the MoneyBeast Machine projects. It is the engineering/governance layer, not a second copy of the products themselves.

## Where to start

- Shared capability and worker registry: [MBM/Registry](MBM/Registry/)
- Setup helper: [install.sh](install.sh)
- Engineering scripts: [scripts](scripts/)
- Templates: [templates](templates/)
- Cross-project mission and customer priorities: [Jarvis Operations Hub](https://github.com/MohammedAbdelshafy/jarvis-mbm)

## Working rules

- Check the owning product repo before editing production behavior.
- Keep one authoritative implementation per subsystem.
- Preserve data provenance, suppression, approval gates and single-writer boundaries.
- Do not install third-party tools until their license, security and actual need are checked.
- Record operational facts as verified, inferred or unknown.
- Use plain, outcome-focused language in anything a customer will see.

This repository is the shared method and tooling. Product code, sales pages and customer delivery stay with their canonical project owners.
