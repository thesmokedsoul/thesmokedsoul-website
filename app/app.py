import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail, Message

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-change-me")

# -------------------------
# EMAIL CONFIG (Gmail example)
# -------------------------
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")  # your email
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")  # app password (NOT your normal password)
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")

mail = Mail(app)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit-booking", methods=["POST"])
def submit_booking():
    try:
        name = request.form.get("name")
        email = request.form.get("email")
        event_type = request.form.get("event_type")
        date = request.form.get("date")
        guests = request.form.get("guests")
        budget = request.form.get("budget")
        details = request.form.get("details")

        msg = Message(
            subject=f"🔥 New Smoked Soul Booking Request: {event_type}",
            recipients=[os.getenv("MAIL_USERNAME")]
        )

        msg.body = f"""
New Booking Inquiry — The Smoked Soul

Name: {name}
Email: {email}
Event Type: {event_type}
Date: {date}
Guests: {guests}
Budget: {budget}

Details:
{details}
"""

        mail.send(msg)

        return redirect(url_for("home") + "#booking")

    except Exception as e:
        print(e)
        return "Error sending booking request", 500


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)