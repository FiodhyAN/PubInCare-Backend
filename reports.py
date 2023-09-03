from flask import request, jsonify
from werkzeug.utils import secure_filename
import psycopg2
import os
import random
from datetime import datetime

UPLOAD_FOLDER = "./images"
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])

def db_conn():
    conn = psycopg2.connect(database="PubInCare-Backend", host="localhost", port="5432", user="postgres", password="dbnyafio")
    return conn

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def create_report():
    jenis_pengaduan = request.form["jenis_pengaduan"]
    timestamp = int(datetime.now().timestamp())
    random_number = random.randint(100, 999)
    if jenis_pengaduan == "Perbaikan":
        no_laporan = f"PRB_{timestamp}_{random_number}"
    else:
        no_laporan = f"PNG_{timestamp}_{random_number}"
    user_id = request.form["user_id"]
    file = request.files["image_url"]
    nama_pengadu = request.form["nama_pengadu"]
    lokasi = request.form["lokasi"]
    keluhan = request.form["keluhan"]
    if file and allowed_file(file.filename) and nama_pengadu and jenis_pengaduan and lokasi and keluhan:
        filetype = file.filename.rsplit(".", 1)[1].lower()
        filename = f"Report_{int(datetime.now().timestamp())}.{filetype}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        image_url = filename
        conn = db_conn()
        cur = conn.cursor()
        while True:
            cur.execute("SELECT * FROM reports WHERE no_laporan = %s", (no_laporan,))
            if cur.fetchone() is None:
                break
            else:
                timestamp = int(datetime.now().timestamp())
                random_number = random.randint(100, 999)
                if jenis_pengaduan == "Perbaikan":
                    no_laporan = f"PRB_{timestamp}_{random_number}"
                else:
                    no_laporan = f"PNG_{timestamp}_{random_number}"
        cur.execute("INSERT INTO reports (user_id, no_laporan, nama_pengadu, jenis_pengaduan, lokasi, keluhan, image_url, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (user_id, no_laporan, nama_pengadu, jenis_pengaduan, lokasi, keluhan, image_url, datetime.now(), datetime.now()))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "No Pengaduan " + no_laporan + " Telah Kami Terima"}), 201
    else:
        return jsonify({"message": "Image only"}), 400
    
def get_reports():
    user = request.args.get("user")
    conn = db_conn()
    cur = conn.cursor()
    if user:
        cur.execute("SELECT id, no_laporan, status, lokasi, image_url FROM reports WHERE user_id = %s", (user,))
    else:
        return jsonify({"message": "User not found"}), 404
    rows = cur.fetchall()
    if rows:
        reports = []
        for row in rows:
            reports.append({
                "id": row[0],
                "no_laporan": row[1],
                "status": row[2],
                "lokasi": row[3],
                "image_url": row[4]
            })
        return jsonify(reports), 200
    else:
        return jsonify({"message": "Report not found"}), 404