from flask import request, jsonify
from werkzeug.utils import secure_filename
import psycopg2
import os
import random
from datetime import datetime
from tensorflow.keras.applications.imagenet_utils import preprocess_input, decode_predictions
from tensorflow.keras.models import load_model, model_from_json
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np

MODEL_ARCHITECTURE = 'PubInCare.json'
MODEL_WEIGHTS = 'PubInCare.h5'
PREDICTION_CLASSES = {
    0: ('normal', 'health.html'),
    1: ('potholes', 'tidakad.html'),
}

def load_model_from_file():
    json_file = open(MODEL_ARCHITECTURE, 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    model = model_from_json(loaded_model_json)
    model.load_weights(MODEL_WEIGHTS)
    return model

model = load_model_from_file()

def model_predict(img_path, model):
    test_image = load_img(img_path, target_size=(224, 224))
    print("@@ Got Image for prediction")

    test_image = img_to_array(test_image) / 255
    test_image = np.expand_dims(test_image, axis=0)

    result = model.predict(test_image)
    pred = np.argmax(result, axis=1)
    return PREDICTION_CLASSES[pred[0]]

UPLOAD_FOLDER = "./images"
ALLOWED_EXTENSIONS = set(["png", "jpg", "jpeg"])

def db_conn():
    conn = psycopg2.connect(database="PubInCare-Backend", host="localhost", port="5432", user="postgres", password="dbnyafio")
    return conn

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def create_report():
    jenis_pengaduan = request.form["jenis_pengaduan"]

    file = request.files["image_url"]
    filetype = file.filename.rsplit(".", 1)[1].lower()
    filename = f"Report_{int(datetime.now().timestamp())}.{filetype}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(os.path.join(UPLOAD_FOLDER, filename))

    if jenis_pengaduan == "Perbaikan":
        sistem_status = model_predict(filepath, model)
        if sistem_status[0] == "normal":
            status = False
        else:
            status = True
    timestamp = int(datetime.now().timestamp())
    random_number = random.randint(100, 999)
    if jenis_pengaduan == "Perbaikan":
        no_laporan = f"PRB_{timestamp}_{random_number}"
    else:
        no_laporan = f"PNG_{timestamp}_{random_number}"
    user_id = request.form["user_id"]
    nama_pengadu = request.form["nama_pengadu"]
    lokasi = request.form["lokasi"]
    keluhan = request.form["keluhan"]
    if file and allowed_file(file.filename) and nama_pengadu and jenis_pengaduan and lokasi and keluhan:
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
        if jenis_pengaduan == "Perbaikan":
            cur.execute("INSERT INTO reports (user_id, no_laporan, nama_pengadu, jenis_pengaduan, lokasi, keluhan, image_url, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (user_id, no_laporan, nama_pengadu, jenis_pengaduan, lokasi, keluhan, image_url, status, datetime.now(), datetime.now()))
        else:
            cur.execute("INSERT INTO reports (user_id, no_laporan, nama_pengadu, jenis_pengaduan, lokasi, keluhan, image_url, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (user_id, no_laporan, nama_pengadu, jenis_pengaduan, lokasi, keluhan, image_url, datetime.now(), datetime.now()))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"message": "No Pengaduan " + no_laporan + " Telah Kami Terima"}), 201
    else:
        return jsonify({"message": "Image only"}), 400
    
def get_reports():
    user = request.args.get("user")
    search = request.args.get("search")
    conn = db_conn()
    cur = conn.cursor()
    if user:
        if search:
            cur.execute("SELECT id, no_laporan, status, lokasi, image_url FROM reports WHERE user_id = %s AND (no_laporan ILIKE %s OR lokasi ILIKE %s)", (user, "%" + search + "%", "%" + search + "%"))
        else:
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