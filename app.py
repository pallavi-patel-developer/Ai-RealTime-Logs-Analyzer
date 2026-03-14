import flask
from flask import render_template
import os
import threading
import logging
import traceback
import sys
from datetime import datetime
from dotenv import load_dotenv

# For cross-platform file locking (Production safety)
try:
    if os.name == 'nt':
        import msvcrt
    else:
        import fcntl
except ImportError:
    msvcrt = fcntl = None

# Load environment variables BEFORE importing analyzer
load_dotenv()

from werkzeug.exceptions import HTTPException
from analyzer import monitor_logs

app = flask.Flask(__name__)

# Use relative path for portability (Render/Windows)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_LOG_FILE = os.path.join(BASE_DIR, "server.log")
LOCK_FILE = os.path.join(BASE_DIR, "monitor.lock")

def acquire_lock():
    """Ensures only one process runs the monitor thread."""
    try:
        f = open(LOCK_FILE, 'w')
        if os.name == 'nt':
            if msvcrt:
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            if fcntl:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return f
    except (IOError, ImportError):
        return None

def get_client_ip():
    """Extracts the real client IP, considering proxies like Render."""
    if flask.request.headers.get('X-Forwarded-For'):
        # Usually the first IP in the list is the original client
        return flask.request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return flask.request.remote_addr

# Start the background log monitor thread with a lock
lock_f = acquire_lock()
if lock_f:
    monitor_thread = threading.Thread(target=monitor_logs, daemon=True)
    monitor_thread.start()
    print("INFO: Log Monitor Started (Process Lock Acquired).")
else:
    print("INFO: Log Monitor skipped (Another process is monitoring).")


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/about", methods=["GET"])
def about():
    # Simulated Server Error for testing alerts
    return "Simulated Server Error on About Page!", 500

@app.route("/dashboard", methods=["GET"])
def dashboard():
    return "Dashboard Page"    

@app.route("/login", methods=["GET"])
def login():
    # Example: Simulating a failed login with status 401
    auth = flask.request.args.get('auth')
    if auth == 'fail':
        return "Unauthorized Access!", 401
    return "Login Page"    

@app.route("/checkout", methods=["GET"])
def checkout():
    return "Checkout Page"    

@app.route("/api/data", methods=["GET"])
def api_data():
    return "API Data Page"    

@app.route("/force-error", methods=["GET"])
def force_error():
    result = 1 / 0 
    return "This won't be reached", 200

@app.errorhandler(Exception)
def handle_unexpected_error(e):
    # If the error is an HTTPException (like 404), we should NOT treat it as a crash
    if isinstance(e, HTTPException):
        return e

    # Otherwise, it's a real code crash (500)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tb = traceback.format_exc()
    
    log_entry = f"{timestamp} | ERROR_TRACEBACK | {flask.request.path} | EXCEPTION: {str(e)}\n{tb}\n"
    
    with open(SERVER_LOG_FILE, "a") as f:
        f.write(log_entry)
        
    return "Internal Server Error!", 500

@app.after_request
def log_request_info(response):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip = get_client_ip()
    method = flask.request.method
    path = flask.request.path
    status_code = response.status_code
    
    status_messages = {
        200: "OK", 201: "CREATED", 204: "NO CONTENT",
        301: "MOVED PERMANENTLY", 302: "FOUND",
        400: "BAD REQUEST", 401: "UNAUTHORIZED", 403: "FORBIDDEN",
        404: "NOT FOUND", 405: "METHOD NOT ALLOWED",
        422: "UNPROCESSABLE ENTITY", 429: "TOO MANY REQUESTS",
        500: "INTERNAL SERVER ERROR", 502: "BAD GATEWAY",
        503: "SERVICE UNAVAILABLE", 504: "GATEWAY TIMEOUT"
    }
    message = status_messages.get(status_code, "UNKNOWN ERROR")

    log_line = f"{timestamp} | {ip} | {method} | {path} | {status_code} | {message}\n"

    with open(SERVER_LOG_FILE, "a") as f:
        f.write(log_line)

    return response

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
