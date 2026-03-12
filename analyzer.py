import os
import re
import time
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "server.log")

# These will be set in Render Environment Variables
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD") # App Password
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")

def send_alert_email(subject, body):
    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
        print("DEBUG: Email credentials missing. Notification not sent.")
        return

    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print(f"SUCCESS: Alert email sent to {EMAIL_RECEIVER}")
    except Exception as e:
        print(f"ERROR: Failed to send email: {e}")

def monitor_logs():
    print("STARTING: Background Log Monitor...")
    
    # Ensure log file exists
    if not os.path.exists(LOG_FILE):
        open(LOG_FILE, 'a').close()

    # Regex to match: 2026-03-12 19:42:31 | 127.0.0.1 | GET | /checkout | 200 | OK
    log_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) \| ([\d\.]+) \| (\w+) \| (/[^ ]*) \| (\d+) \| (.*)")

    with open(LOG_FILE, 'r') as f:
        # Move pointer to end of file to start monitoring new entries
        f.seek(0, 2)
        
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue

            match = log_pattern.match(line.strip())
            if match:
                timestamp, ip, method, path, status, message = match.groups()
                status = int(status)

                # TRIGGER: Critical Server Error
                if status == 500:
                    subject = f"🚨 CRITICAL: Server Error (500) detected!"
                    body = f"Time: {timestamp}\nIP: {ip}\nMethod: {method}\nPath: {path}\nLog: {line}"
                    send_alert_email(subject, body)

                # TRIGGER: Potential Security Threat (Example: multiple 404s or unauthorized)
                if status == 401:
                    subject = f"⚠️ SECURITY: Unauthorized Access Attempt"
                    body = f"An unauthorized attempt was detected!\n\nDetails:\nTime: {timestamp}\nIP: {ip}\nPath: {path}"
                    send_alert_email(subject, body)

if __name__ == "__main__":
    # Test local run
    monitor_logs()
