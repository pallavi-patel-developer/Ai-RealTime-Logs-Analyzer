import os
import re
import time
import resend
from datetime import datetime

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "server.log")

# These will be set in Render Environment Variables
def get_env_vars():
    return os.environ.get("RESEND_API_KEY"), os.environ.get("CLINIC_EMAIL")

def send_alert_email(subject, body):
    resend_api_key, clinic_email = get_env_vars()
    if not resend_api_key or not clinic_email:
        print("DEBUG: Resend API credentials or Clinic Email missing. Notification not sent.")
        return

    try:
        resend.api_key = resend_api_key
        
        params = {
            "from": "AI Log Analyzer <onboarding@resend.dev>",
            "to": [clinic_email],
            "subject": subject,
            "html": f"<pre>{body}</pre>",
        }

        email = resend.Emails.send(params)
    except Exception as e:
        print(f"ERROR")


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

            # Check for multi-line traceback starts
            if " | ERROR_TRACEBACK | " in line:
                try:
                    path = line.split(" | ")[2]
                    traceback_content = line
                    # Read next lines until we hit a signature of a new log entry
                    while True:
                        next_line = f.readline()
                        if not next_line:
                            time.sleep(0.1)
                            next_line = f.readline()
                            if not next_line: break
                        traceback_content += next_line
                        # Stop if we see a new timestamp or a separator
                        if " | " in next_line and re.match(r"\d{4}-\d{2}-\d{2}", next_line):
                             break
                    
                    subject = f" PRODUCTION ALERT: Traceback in {path}"
                    send_alert_email(subject, traceback_content)
                except Exception as e:
                    print(f"DEBUG: Error parsing traceback block: {e}")
                continue

            match = log_pattern.match(line.strip())
            if match:
                timestamp, ip, method, path, status, message = match.groups()
                status = int(status)

                # TRIGGER: Critical Server Error
                if status == 500:
                    subject = f" CRITICAL: Server Error (500) detected!"
                    body = f"Time: {timestamp}\nIP: {ip}\nMethod: {method}\nPath: {path}\nLog: {line}"
                    send_alert_email(subject, body)

                # TRIGGER: Potential Security Threat (Example: multiple 404s or unauthorized)
                if status == 401:
                    subject = f" SECURITY: Unauthorized Access Attempt"
                    body = f"An unauthorized attempt was detected!\n\nDetails:\nTime: {timestamp}\nIP: {ip}\nPath: {path}"
                    send_alert_email(subject, body)

if __name__ == "__main__":
    # Test local run
    monitor_logs()
