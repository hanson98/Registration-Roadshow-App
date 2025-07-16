from flask import Flask, render_template, redirect, url_for
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
        msg = (
            f"Hi {data['name']},\n\n"
            "Thank you for expressing your interest and registering for this exclusive property invitation."
            "Our team will be in touch shortly to provide comprehensive details and discuss how our expert property advisors can assist you.\n\n"
            "For immediate assistance, please feel free to contact us at 016-2132-712.\n\n"
            "Regards,\n"
            "IX Group,\n"
            "May Tang"
        )
        print(data["phone"])
        try:
            message = client.messages.create(
                body=msg,
                from_="whatsapp:+14155238886",
                to=f"whatsapp:+6{data['phone']}",
            )
            print(message.status)
        except:
            pass

        return redirect(url_for("success"))
    return render_template("register.html", form=form)


@app.route("/success")
def success():
    return render_template("register_success.html")


if __name__ == "__main__":
    app.run()
