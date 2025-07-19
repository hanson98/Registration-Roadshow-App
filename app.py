from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import (
    Bootstrap5,
)  # Optional if you're using your own Bootstrap via CDN
from flask_wtf import FlaskForm
from wtforms import StringField, TelField, SubmitField
from wtforms.validators import InputRequired, Optional, Email, Regexp
import requests
from dotenv import load_dotenv
import os
from twilio.rest import Client
import time


load_dotenv()
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
bootstrap = Bootstrap5(app)  # You can keep or remove this if not using `render_form`


class ResigterForm(FlaskForm):
    phone = TelField(
        "Phone Number",
        validators=[
            InputRequired(message="Phone number is required."),
            Regexp(r"^\+?\d[\d\s\-]{8,14}$", message="Enter a valid phone number."),
        ],
        filters=[lambda x: x.strip() if x else x],
    )
    name = StringField(
        "Name",
        validators=[InputRequired()],
        filters=[lambda x: x.strip() if x else x],
    )
    email = StringField(
        "Email",
        validators=[Optional(), Email(message="Enter a valid email address.")],
        filters=[lambda x: x.strip() if x else x],
    )
    submit = SubmitField("Submit")


@app.route("/", methods=["GET", "POST"])
def registration():
    form = ResigterForm()
    if form.validate_on_submit():
        data = {
            "phone": form.phone.data,
            "name": form.name.data,
            "email": form.email.data,
        }
        SHEET_WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbyA-vqiJlOeswFbvXBkP6kmMvyHvnCarCY9bA_okqWdtQ7dPGFpD0sI989b1f1UJIHM2g/exec"
        response = requests.post(SHEET_WEBHOOK_URL, json=data)
        response.raise_for_status()

        account_sid = os.environ["TWILIO_ACCOUNT_SID"]
        auth_token = os.environ["TWILIO_AUTH_TOKEN"]
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=f"Prospect Name: {data['name']},\n\nNumber: {data['phone']}",
            from_="whatsapp:+14155238886",
            to=f"whatsapp:+60162132712",
        )

        msg = (
            f"Hi {data['name']},\n\n"
            "Thank you for registering your interest in our exclusive property project near KLCC.\n"
            "Our team will reach out shortly with full details and to explore how our expert advisors can assist you.\n\n"
            "If you have any questions in the meantime, feel free to WhatsApp or call us at 016-2132-712.\n\n"
            "Warm regards,\n"
            "May Tang\n"
            "IX Group"
        )

        time.sleep(0.5)

        print(data["phone"])
        try:
            message = client.messages.create(
                body=msg,
                from_="whatsapp:+14155238886",
                to=f"whatsapp:+60162132712",
            )
            print(message.status)
        except:
            pass

        print("Data being sent to success page:", data["name"])
        return redirect(url_for("success", name=data["name"]))
    return render_template("register.html", form=form)


@app.route("/success")
def success():
    name = request.args.get("name", "there")
    return render_template("register_success.html", name=name)


if __name__ == "__main__":
    app.run()
