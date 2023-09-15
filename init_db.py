import psycopg2

conn = psycopg2.connect(database="PubInCare-Backend", host="localhost", port="5432", user="postgres", password="dbnyafio")
cur = conn.cursor()

# create the database
# cur.execute(''' CREATE TABLE IF NOT EXISTS users (id serial PRIMARY KEY, name varchar(255), email varchar(255), password varchar(255), role varchar(255), created_at timestamp, updated_at timestamp)''')

# refresh the database
cur.execute(''' DROP TABLE IF EXISTS users ''')
cur.execute(''' CREATE TABLE IF NOT EXISTS users (id serial PRIMARY KEY, name varchar(255), email varchar(255), password varchar(255), role varchar(255), profile_image varchar(255), created_at timestamp, updated_at timestamp)''')

cur.execute(''' DROP TABLE IF EXISTS reports ''')
cur.execute(''' CREATE TABLE IF NOT EXISTS reports (id serial PRIMARY KEY, no_laporan varchar(255), user_id integer, nama_pengadu varchar(255), jenis_pengaduan varchar(255), lokasi text, keluhan text, image_url varchar(255), status boolean, created_at timestamp, updated_at timestamp)''')

conn.commit()
cur.close()
conn.close()