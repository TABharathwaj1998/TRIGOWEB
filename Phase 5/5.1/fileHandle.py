from flask import Flask, request,render_template
import os
import psycopg2
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__,template_folder="template")

conn = psycopg2.connect(host="localhost", port=5432, database="postgres", user="postgres", password="Rise@1998")
cur = conn.cursor()

UPLOAD_FOLDER = 'C:/Users/tabha/Documents/Python/uploadFiles'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    cur.execute("CREATE TABLE IF NOT EXISTS images(No INTEGER, image BYTEA)")
    conn.commit()
    return render_template("upload.html")

@app.route('/upload',methods = ["POST","GET"])
def uploadImg():
    if request.method=="POST":
        flag = 0
        file = request.files.getlist("filename[]")
        print(file)

        for f in file:
            flag = flag + 1
            file = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], file))
            cur.execute("INSERT INTO images(no,image) VALUES(%s,%s)",(flag, file))
            conn.commit()
        return "File received"
    
@app.route('/display')
def display():
    cur.execute("SELECT * FROM images")
    img = cur.fetchall()

    BLOB = img[0][1]
    print(BLOB)
    open("FromDB.txt", 'wb').write(BLOB)
    image = open("FromDB.txt",'r').read()
    print(image)
    nature = Image.open(image)
    nature.load()
    nature.show("NatureSample")
    return "Image retrieved"


if __name__ == "main":
    app.run() 