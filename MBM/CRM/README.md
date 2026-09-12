# CRM — File-based, git-versioned

One JSON file per lead in `leads/`. Research in `intel/`, proposals in `proposals/`, outreach & marketing content in `content/`. Integrity rules live in `Workers/08-crm-brain.md`. Validate with `bash scripts/mbm.sh validate`.

## Lead schema (`leads/L-YYYY-NNNN-<slug>.json`)

```json
{
  "id": "L-2026-0001",
  "company": "Example Contracting Co",
  "domain": "example-co.com",
  "website": "https://example-co.com",
  "industry": "construction",
  "geography": "Egypt",
  "size": "51-200",
  "language": "ar",
  "source": "wuzzuf job posting",
  "signals": [
    {"date": "2026-07-01", "signal": "Hiring 3 document controllers for New Capital project", "url": "https://..."}
  ],
  "contacts": [
    {"name": "", "title": "Operations Director", "email": "", "linkedin": "", "entry_contact": true, "notes": ""}
  ],
  "pain_points": [
    {"pain": "Manual site-report consolidation", "status": "verified", "source": "https://..."}
  ],
  "fit_score": 72,
  "stage": "new",
  "owner": "",
  "next_action": {"date": "2026-07-07", "action": "Company Researcher: full intel report"},
  "estimated_value": 0,
  "won": null,
  "lost_reason": null,
  "relationships": [],
  "history": [
    {"date": "2026-07-04", "actor": "lead-hunter", "event": "created", "note": "found via wuzzuf hiring signal"}
  ]
}
```

### Field rules
- `industry`: `construction | industrial | recycling | ports | manufacturing | ai-automation | b2b-services`
- `stage`: `new → researched → contacted → replied → meeting → proposal → won | lost` (forward-only; see CRM Brain rules)
- `fit_score`: 0–100 per the rubric in `Knowledge_Base/offer.md`; **qualified = ≥ 60**
- `estimated_value`: USD, set when stage ≥ meeting; feeds `pipeline_value` on the dashboard
- `won`: `{"date": "...", "value": 5000, "recurring_monthly": 1500}` when stage = won
- `language`: `ar | en` — Outreach Agent writes in this language
- `history[]`: append-only; every touch by any worker or human

## ID allocation
`scripts/mbm.sh lead add "<Company>"` allocates the next `L-YYYY-NNNN`, creates a stub file, and files a research mission if you pass `--score ≥ 60`. Manual creation is fine too — just keep IDs unique and run `validate`.
