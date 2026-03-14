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

def get_html_template(level, title, details, traceback=None):
    
    colors = {
        "CRITICAL": "#ef4444", # Red
        "SECURITY": "#f97316", # Orange
        "INFO": "#6366f1"      # Indigo
    }
    color = colors.get(level, "#6366f1")
    
    traceback_html = ""
    if traceback:
        traceback_html = f"""
        <div style="margin-top: 20px; padding: 15px; background: #1e293b; border-radius: 8px; border: 1px solid #334155;">
            <h3 style="color: #94a3b8; font-size: 14px; margin-bottom: 10px; text-transform: uppercase;">Stack Traceback</h3>
            <pre style="color: #cbd5e1; font-family: 'Courier New', monospace; font-size: 13px; white-space: pre-wrap; margin: 0;">{traceback}</pre>
        </div>
        """

    details_html = ""
    for key, val in details.items():
        details_html += f"""
        <tr>
            <td style="padding: 8px 0; color: #94a3b8; font-size: 14px; width: 100px;"><strong>{key}:</strong></td>
            <td style="padding: 8px 0; color: #f8fafc; font-size: 14px;">{val}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #0f172a; margin: 0; padding: 0; }}
        </style>
    </head>
    <body style="background-color: #0f172a; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background: #1e293b; border-radius: 16px; overflow: hidden; border: 1px solid #334155; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);">
            <div style="background: {color}; padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0; font-size: 24px; letter-spacing: -0.02em;">AI Log Analyzer</h1>
                <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0; font-size: 16px;">{title}</p>
            </div>
            <div style="padding: 30px;">
                <table style="width: 100%; border-collapse: collapse;">
                    {details_html}
                </table>
                {traceback_html}
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #334155; text-align: center;">
                    <p style="color: #64748b; font-size: 12px; margin: 0;">This is an automated production alert from your AI Real-Time Monitor.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

def send_alert_email(subject, title, level, details, traceback=None):
    resend_api_key, clinic_email = get_env_vars()
    if not resend_api_key or not clinic_email:
        print("DEBUG: Resend API credentials or Clinic Email missing. Notification not sent.")
        return

    try:
        resend.api_key = resend_api_key
        html_content = get_html_template(level, title, details, traceback)
        
        params = {
            "from": "AI Log Analyzer <onboarding@resend.dev>",
            "to": [clinic_email],
            "subject": subject,
            "html": html_content,
        }

        email = resend.Emails.send(params)
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

            if " | ERROR_TRACEBACK | " in line:
                try:
                    parts = line.split(" | ")
                    timestamp = parts[0]
                    path = parts[2]
                    traceback_content = line

                    while True:
                        next_line = f.readline()
                        if not next_line:
                            time.sleep(0.1)
                            next_line = f.readline()
                            if not next_line: break
                        traceback_content += next_line
                        if " | " in next_line and re.match(r"\d{4}-\d{2}-\d{2}", next_line):
                             break
                    
                    subject = f" CRITICAL: Traceback in {path}"
                    details = {
                        "Timestamp": timestamp,
                        "Endpoint": path,
                        "Type": "Python Exception"
                    }
                    send_alert_email(subject, "Critical Runtime Exception", "CRITICAL", details, traceback_content)
                except Exception as e:
                    print(f"DEBUG: Error parsing traceback block: {e}")
                continue

            match = log_pattern.match(line.strip())
            if match:
                timestamp, ip, method, path, status, message = match.groups()
                status = int(status)

                if status == 500:
                    subject = f" CRITICAL: Server Error (500) detected!"
                    details = {
                        "Timestamp": timestamp,
                        "IP Address": ip,
                        "Method": method,
                        "Endpoint": path,
                        "Status": status
                    }
                    send_alert_email(subject, "Server Error Detected", "CRITICAL", details)
                if status == 401:
                    subject = f" SECURITY: Unauthorized Access Attempt"
                    details = {
                        "Timestamp": timestamp,
                        "IP Address": ip,
                        "Method": method,
                        "Endpoint": path,
                        "Status": "401 Unauthorized"
                    }
                    send_alert_email(subject, "Security Warning", "SECURITY", details)

if __name__ == "__main__":
    monitor_logs()
