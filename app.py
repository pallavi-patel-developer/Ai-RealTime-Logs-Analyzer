import flask, logging
import json
from datetime import datetime
import os
app = flask.Flask(__name__)

# Use relative path for portability (Render/Windows)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_LOG_FILE = os.path.join(BASE_DIR, "server.log")

#  @app.after_request function tab chalta hai jab Browser se server par request aati hai aur server usko data bhejne hi wala hota hai. Hum is function ko intercept karke details nikal lenge:
# flask.request.remote_addr (Aapka IP, normally '127.0.0.1')
# flask.request.method (GET/POST)
# flask.request.path (/home, /login etc.)
# Status Code (200, 404 etc.)

@app.route("/",methods=["GET"])
def home():
    return "Hello World"

@app.route("/about",methods=["GET"])
def about():
    return "About Page"    

@app.route("/dashboard",methods=["GET"])
def dashboard():
    return "Dashboard Page"    

@app.route("/login",methods=["GET"])
def login():
    return "Login Page"    

@app.route("/checkout",methods=["GET"])
def checkout():
    return "Checkout Page"    

@app.route("/api/data",methods=["GET"])
def api_data():
    return "API Data Page"    
    
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

# Note: Aapko werkzeug (default flask logging) ko band karna padega warna file me duplicate kachra jayega.
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

if __name__ == "__main__":
    # main()
    app.run(debug=True)
