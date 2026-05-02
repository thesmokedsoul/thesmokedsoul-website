from flask import Flask, request, jsonify, send_from_directory, render_template, Response
import csv
import os
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import pickle
import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from functools import wraps

app = Flask(__name__, static_folder="static")

# -----------------------------
# CONFIG
# -----------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]
GOOGLE_CREDS_FILE = "smoked-soul-writer.json"
SPREADSHEET_NAME = "The Smoked Soul Leads"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "bookings.csv")

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "chef")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "change-this-password")


def check_auth(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD


def require_admin_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization

        if not auth or not check_auth(auth.username, auth.password):
            return Response(
                "Admin access requires login.",
                401,
                {"WWW-Authenticate": 'Basic realm="The Smoked Soul Admin"'}
            )

        return f(*args, **kwargs)

    return decorated

# -----------------------------
# CSV SETUP
# -----------------------------
if not os.path.exists("bookings.csv"):
    with open("bookings.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "name",
            "email",
            "event_type",
            "date",
            "guests",
            "budget",
            "details"
        ])

# -----------------------------
# GOOGLE SHEETS FUNCTIONS
# -----------------------------
def get_gsheet_client():
    creds = Credentials.from_service_account_file(
        GOOGLE_CREDS_FILE,
        scopes=SCOPES
    )
    return gspread.authorize(creds)


def append_to_sheet(row):
    try:
        client = get_gsheet_client()
        sheet = client.open(SPREADSHEET_NAME).sheet1
        sheet.append_row(row)
        print("✅ Google Sheets write SUCCESS")
    except Exception as e:
        print("❌ Google Sheets error:", e)

SCOPES_GMAIL = ["https://www.googleapis.com/auth/gmail.send"]

def get_gmail_service():
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "gmail_credentials.json",
                SCOPES_GMAIL
            )
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)


def send_confirmation_email(to_email):
    service = get_gmail_service()

    msg = MIMEText("You are on the board. We will be in touch shortly.")
    msg["to"] = to_email
    msg["subject"] = "The Smoked Soul – Booking Received"

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()

    print("📧 Email sent to client")

# -----------------------------
# ROUTES
# -----------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/story")
def story():
    return render_template("story.html")


@app.route("/experience")
def experience():
    return render_template("experience.html")


@app.route("/goods")
def goods():
    return render_template("goods.html")


@app.route("/submit-booking", methods=["POST"])
def submit_booking():
    data = request.form

    row = [
        datetime.now().isoformat(),
        data.get("name", ""),
        data.get("email", ""),
        data.get("event_type", ""),
        data.get("date", ""),
        data.get("guests", ""),
        data.get("budget", ""),
        data.get("details", ""),
        "NEW"
    ]

    # Save to CSV (backup)
    with open(CSV_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)

    # Save to Google Sheets
    append_to_sheet(row)

    # Send confirmation email (safe fail)
    email = data.get("email")
    if email:
        try:
            send_confirmation_email(email)
        except Exception as e:
            print(f"Email failed: {e}")

    return jsonify({
        "status": "success",
        "message": "You are on the board. We will be in touch shortly.",
        "redirect": "/thank-you"
    })

# -----------------------------
# ADMIN AUTH CONFIG
# -----------------------------
@app.route("/admin")
@require_admin_auth
def admin_dashboard():

    with open(CSV_PATH, newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        return render_template("admin.html", bookings=[])

    header = rows[0]
    data_rows = rows[1:]

    bookings = list(enumerate(data_rows))

    return render_template("admin.html", bookings=bookings)


@app.route("/update-status")
@require_admin_auth
def update_status():
    try:
        row_index = int(request.args.get("row"))
        new_status = request.args.get("status", "NEW").strip()

        with open(CSV_PATH, newline="") as f:
            rows = list(csv.reader(f))

        if not rows or len(rows) < 2:
            return ("No data", 400)

        header = rows[0]
        data_rows = rows[1:]

        if row_index < 0 or row_index >= len(data_rows):
            return ("Invalid row", 400)

        while len(data_rows[row_index]) < 9:
            data_rows[row_index].append("NEW")

        data_rows[row_index][8] = new_status

        with open(CSV_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(data_rows)

        return ("", 204)

    except Exception as e:
        print("STATUS ERROR:", e)
        return ("Error", 500)


@app.route("/thank-you")
def thank_you():
    return render_template("thank-you.html")

# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

print(app.url_map)