import psycopg2
import mimetypes
from flask import Flask, request, jsonify, send_file
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from auth import register, login, changePW
from reports import create_report, get_reports

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

@app.route("/change-password", methods=["PUT"])
def change_password_route():
    return changePW()

@app.route("/reports/store", methods=["POST"])
def create_report_route():
    return create_report()

@app.route("/reports", methods=["GET"])
def get_reports_route():
    return get_reports()

@app.route("/images/<filename>")
def get_image(filename):
    file_path = f"./images/{filename}"
    mimetype, _ = mimetypes.guess_type(file_path)
    
    if mimetype is None:
        mimetype = 'application/octet-stream'  # Default to binary if mimetype cannot be determined

    return send_file(file_path, mimetype=mimetype)


if __name__ == "__main__":
    app.run(debug=True)
