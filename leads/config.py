import os

# ATTOM Data API — get your key at https://api.attomdata.com
ATTOM_API_KEY = os.getenv("ATTOM_API_KEY", "")

# Email delivery (for the daily client pipeline)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")

# Output directory for CSV exports
OUTPUT_DIR = os.getenv("LEADS_OUTPUT_DIR", "output")

# Lead types to pull
LEAD_TYPES = ["pre-foreclosure", "distressed", "reo"]
