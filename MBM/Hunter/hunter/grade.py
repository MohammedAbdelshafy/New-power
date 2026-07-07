"""Deterministic lead grading — Platinum -> Bronze.

Pure functions, no I/O. This is the rubric the whole business depends on, so it is
transparent, testable, and free of hidden state. Weights live in `models.py`.
"""

from __future__ import annotations

from .models import Lead, Grade, SIGNAL_WEIGHTS, CONTACT_WEIGHTS

# score >= threshold  ->  grade  (checked top-down)
GRADE_RULES: list[tuple[int, Grade]] = [
    (80, Grade.PLATINUM),
    (55, Grade.GOLD),
    (30, Grade.SILVER),
    (0, Grade.BRONZE),
]


def score_lead(lead: Lead) -> tuple[int, list[str]]:
    """Return (score, human-readable reasons) for a lead. No mutation."""
    score = 0
    reasons: list[str] = []

    for signal in lead.signals:
        weight = SIGNAL_WEIGHTS.get(signal)
        if weight:
            score += weight
            reasons.append(f"+{weight} {signal}")

    for field_name, weight in CONTACT_WEIGHTS.items():
        if getattr(lead, field_name, ""):
            score += weight
            reasons.append(f"+{weight} {field_name}")

    return score, reasons


def grade_lead(lead: Lead) -> Lead:
    """Score and grade a lead in place, then return it.

    A lead that fails the minimum-data gate is graded REJECT regardless of score —
    an unreachable or unlocatable record is not a sellable lead.
    """
    if not lead.has_min_data():
        lead.score = 0
        lead.grade = Grade.REJECT.value
        lead.grade_reasons = ["reject: missing property location or any contact path"]
        return lead

    score, reasons = score_lead(lead)
    lead.score = score
    for threshold, grade in GRADE_RULES:
        if score >= threshold:
            lead.grade = grade.value
            break
    lead.grade_reasons = reasons or ["no motivation signals; graded on contactability only"]
    return lead


def grade_all(leads: list[Lead]) -> list[Lead]:
    """Grade a batch and return it sorted best-first (Reject sinks to the bottom)."""
    for lead in leads:
        grade_lead(lead)
    order = {g.value: i for i, g in enumerate(
        [Grade.PLATINUM, Grade.GOLD, Grade.SILVER, Grade.BRONZE, Grade.REJECT]
    )}
    return sorted(leads, key=lambda l: (order.get(l.grade, 99), -l.score))
