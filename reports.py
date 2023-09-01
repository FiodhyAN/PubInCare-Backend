from flask import request, jsonify
from werkzeug.utils import secure_filename
import psycopg2
import os
from datetime import datetime

UPLOAD_FOLDER = "./images"
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])

def db_conn():
    conn = psycopg2.connect(database="PubInCare-Backend", host="localhost", port="5432", user="postgres", password="dbnyafio")
    return conn

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def create_report():
    user_id = request.form["user_id"]
    file = request.files["image_url"]
    nama_pengadu = request.form["nama_pengadu"]
    jenis_pengaduan = request.form["jenis_pengaduan"]
    lokasi = request.form["lokasi"]
    keluhan = request.form["keluhan"]
    status = False
    if file and allowed_file(file.filename) and nama_pengadu and jenis_pengaduan and lokasi and keluhan:
        filetype = file.filename.rsplit(".", 1)[1].lower()
        filename = f"Report_{int(datetime.now().timestamp())}.{filetype}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        image_url = "http://localhost:5000/images/" + filename
        conn = db_conn()
        cur = conn.cursor()
        cur.execute("INSERT INTO reports (user_id, nama_pengadu, jenis_pengaduan, lokasi, keluhan, image_url, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (user_id, nama_pengadu, jenis_pengaduan, lokasi, keluhan, image_url, status, datetime.now(), datetime.now()))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "Pengaduan Anda Telah Kami Terima"}), 201
    else:
        return jsonify({"message": "Image only"}), 400