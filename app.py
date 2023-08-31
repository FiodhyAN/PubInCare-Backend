import psycopg2
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from auth import register, login

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Hello, Flask!"

@app.route("/register", methods=["POST"])
def registration_route():
    return register()

@app.route("/login", methods=["POST"])
def login_route():
    return login()


if __name__ == "__main__":
    app.run(debug=True)
