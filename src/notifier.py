import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict

class Notifier:
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASS")
        self.target_email = os.getenv("ALERT_EMAIL")
        
        self.enabled = all([self.smtp_host, self.smtp_user, self.smtp_pass, self.target_email])

    def send_price_drop_email(self, drops: List[Dict]):
        if not self.enabled:
            print("[Notifier] SMTP not configured. Skipping email alert.")
            print(f"[Notifier] Detected {len(drops)} price drops:")
            for d in drops:
                print(f"  - {d['name']}: ${d['old_price']} -> ${d['new_price']} (-{d['drop']:.1f}%)")
            return

        subject = f"🚨 Price Drop Alert: {len(drops)} Deals Found!"
        
        body = "<h2>Great News! We found some significant price drops:</h2><ul>"
        for d in drops:
            body += f"""
            <li>
                <strong>{d['name']}</strong><br/>
                Was: ${d['old_price']:.2f} | <strong>Now: ${d['new_price']:.2f}</strong><br/>
                <em>Saving: {d['drop']:.1f}%</em><br/>
                <a href="{d['url']}">Buy Now at {d['source']}</a>
            </li><br/>
            """
        body += "</ul><p>View all deals on your <a href='http://localhost:80'>Dashboard</a>.</p>"

        msg = MIMEMultipart()
        msg['From'] = self.smtp_user
        msg['To'] = self.target_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            print(f"[Notifier] Alert email sent to {self.target_email}")
        except Exception as e:
            print(f"[Notifier] Failed to send email: {e}")
