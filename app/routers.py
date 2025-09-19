from app import app
from flask import render_template, url_for

@app.route("/")
@app.route("/index.html")
def home():
    return render_template("index.html")

@app.route("/car-list.html")
def car_list():
    return render_template("car-list.html")

@app.route("/login.html")
def login():
    return render_template("login.html")

@app.route("/registration.html")
def registration():
    return render_template("registration.html")

@app.route("/reserva.html")
def reserva():
    return render_template("reserva.html")

@app.route("/contact.html")
def contact():
    return render_template("contact.html")

