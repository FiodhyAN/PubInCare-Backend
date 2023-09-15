from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
import psycopg2
import re
import os
from reports import allowed_file
from datetime import datetime

UPLOAD_FOLDER = "./images/profile"

bcrypt = Bcrypt()

def db_conn():
    conn = psycopg2.connect(database="PubInCare-Backend", host="localhost", port="5432", user="postgres", password="dbnyafio")
    return conn
def register():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]
    role = 'public'
    if request.method == "POST" and name and email and password:
        conn = db_conn()
        cur = conn.cursor()
        
        cur.execute(''' SELECT * FROM users WHERE email = %s ''', (email,))
        user = cur.fetchone()
        
        if user:
            return jsonify({"message": "Email already exists"}), 400
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            return jsonify({"message": "Invalid email Address"}), 400
        elif len(password) < 6 or (re.search(r'[a-zA-Z]', password) is None) or re.search(r'[0-9]', password) is None:
            return jsonify({"message": "Password must be at least 6 characters long and contain a number and letter"}), 400
        else:
            password = bcrypt.generate_password_hash(password).decode('utf-8')
            cur.execute(''' INSERT INTO users (name, email, password, role, created_at, updated_at) VALUES (%s, %s, %s, %s, NOW(), NOW())''', (name, email, password, role))
            conn.commit()
            cur.close()
            conn.close()
            return jsonify({"message": "Registration Successful Please Login"}), 200
    else:
        return jsonify({"message": "Registration failed wrong method"}), 400
    
def login():
    email = request.form["email"]
    password = request.form["password"]
    if request.method == "POST" and email and password:
        conn = db_conn()
        cur = conn.cursor()
        
        cur.execute(''' SELECT * FROM users WHERE email = %s ''', (email,))
        user = cur.fetchone()
        
        if user:
            if bcrypt.check_password_hash(user[3], password):
                return jsonify({"message": "Success",
                                "user": {
                                    "id": user[0],
                                    "name": user[1],
                                    "email": user[2],
                                    "role": user[4],
                                    "profile_image": user[5]
                                }}), 200
            else:
                return jsonify({"message": "Invalid email or password"}), 400
        else:
            return jsonify({"message": "Invalid email or password"}), 400
    else:
        return jsonify({"message": "Login failed wrong method"}), 400
    
def changePW():
    email = request.form["email"]
    password = request.form["password"]
    confirmPassword = request.form["confirmPassword"]

    if request.method == "PUT" and email and password and confirmPassword:
        conn = db_conn()
        cur = conn.cursor()
        
        cur.execute(''' SELECT * FROM users WHERE email = %s ''', (email,))
        user = cur.fetchone()
        
        if user:
            if password == confirmPassword:
                if len(password) < 6 or (re.search(r'[a-zA-Z]', password) is None) or re.search(r'[0-9]', password) is None:
                    return jsonify({"message": "Password must be at least 6 characters long and contain a number and letter"}), 400
                else:
                    password = bcrypt.generate_password_hash(confirmPassword).decode('utf-8')
                    cur.execute(''' UPDATE users SET password = %s WHERE email = %s ''', (password, email))
                    conn.commit()
                    cur.close()
                    conn.close()
                    return jsonify({"message": "Successfully change password"}), 200
            else:
                return jsonify({"message": "Password and Confirm Password must be same"}), 400
        else:
            return jsonify({"message": "Email not found"}), 400
    else:
        return jsonify({"message": "Change Password failed wrong method"}), 400
    
def store_profile_image():
    if request.method == "POST":
        conn = db_conn()
        cur = conn.cursor()
        
        cur.execute(''' SELECT * FROM users WHERE id = %s ''', (request.form["id"],))
        user = cur.fetchone()
        
        if user:
            profile_image = request.files["profile_image"]
            if request.files and allowed_file(profile_image.filename):
                select_query = """SELECT profile_image FROM users WHERE id = %s"""
                cur.execute(select_query, (request.form["id"],))
                old_profile_image = cur.fetchone()
                if old_profile_image[0] is not None:
                    os.remove(os.path.join(UPLOAD_FOLDER, old_profile_image[0]))

                filetype = profile_image.filename.rsplit(".", 1)[1].lower()
                filename = f"Profile_{request.form['id']}_{int(datetime.now().timestamp())}.{filetype}"
                profile_image.save(os.path.join(UPLOAD_FOLDER, filename))

                cur.execute(''' UPDATE users SET profile_image = %s WHERE id = %s ''', (filename, request.form["id"]))

                cur.execute(''' SELECT id, name, email, role, profile_image FROM users WHERE id = %s ''', (request.form["id"],))
                user_data = cur.fetchone()
                user = {
                    "id": user_data[0],
                    "name": user_data[1],
                    "email": user_data[2],
                    "role": user_data[3],
                    "profile_image": user_data[4]
                }

                conn.commit()
                cur.close()
                conn.close()
                return jsonify(user), 200
            else:
                return jsonify({"message": "No file selected"}), 400
        else:
            return jsonify({"message": "User not found"}), 400
    else:
        return jsonify({"message": "Store profile image failed wrong method"}), 400