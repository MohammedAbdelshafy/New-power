"""MBM Hunter — the lead-intelligence hunting stack.

Tier-1 web-agent tooling (Playwright + Scrapling + MCP) wired into the MBM pipeline:

    fetch  ->  parse  ->  grade (Platinum..Bronze)  ->  LeadPack CSV

The core (parse + grade + pipeline) runs on the standard library alone so it works
in any session with no API keys and no network. Scrapling/Playwright are used for
live fetches when installed; otherwise the pipeline falls back to urllib/local files.
"""

from .models import Lead, Grade
from .grade import grade_lead, GRADE_RULES

__all__ = ["Lead", "Grade", "grade_lead", "GRADE_RULES"]
__version__ = "0.1.0"
