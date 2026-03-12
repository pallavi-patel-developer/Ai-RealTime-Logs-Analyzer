import flask
import os
import threading
import logging
from datetime import datetime
from analyzer import monitor_logs

app = flask.Flask(__name__)

# Use relative path for portability (Render/Windows)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_LOG_FILE = os.path.join(BASE_DIR, "server.log")

# Start the background log monitor thread
# It will run 24/7 scanning the server.log for errors
monitor_thread = threading.Thread(target=monitor_logs, daemon=True)
monitor_thread.start()

@app.route("/", methods=["GET"])
def home():
    return "🚀 Log Analyzer Server is Running!"

@app.route("/about", methods=["GET"])
def about():
    return "About Page"    

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
    # Use this to test the Email alert!
    return "Simulated Server Error!", 500

@app.after_request
def log_request_info(response):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip = flask.request.remote_addr
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

# Disable default flask logging to keep server.log clean
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

if __name__ == "__main__":
    # Render will use Gunicorn to run 'app:app', but for local testing:
    app.run(host='0.0.0.0', port=5000)
