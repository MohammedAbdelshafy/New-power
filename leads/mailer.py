"""Send the daily CSV to a client via email."""

import smtplib
import os
from email.message import EmailMessage
from datetime import datetime


def send_leads(csv_path: str, client_email: str,
               smtp_host: str, smtp_port: int,
               smtp_user: str, smtp_pass: str,
               city: str, state: str):

    today = datetime.now().strftime("%B %d, %Y")
    subject = f"Your Motivated Seller Leads — {city}, {state} ({today})"

    body = f"""Hey,

Your daily motivated-seller leads for {city}, {state} are attached — {today}.

These are pre-foreclosure and distressed properties pulled fresh this morning.
Import the CSV into your CRM, prioritize by equity, and go close some deals.

Questions? Just reply to this email.

Talk soon,
New Power Leads
"""

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"]    = smtp_user
    msg["To"]      = client_email
    msg.set_content(body)

    with open(csv_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="text",
            subtype="csv",
            filename=os.path.basename(csv_path),
        )

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

    print(f"  Delivered to {client_email}")
