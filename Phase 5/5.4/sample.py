from flask import Flask, render_template, request
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, generate_blob_sas, BlobSasPermissions
import os
from werkzeug.utils import secure_filename

app = Flask(__name__,template_folder="template")

number_of_images = 0
UPLOAD_FOLDER = "C:/Users/tabha/Documents/Python/uploadFiles"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template("upload.html")

@app.route("/azureUpload", methods=["POST","GET"])
def azureUpload():
    global number_of_images
    if request.method == "POST":
        files = request.files.getlist("filename[]")
        account_url = "https://tabsamplestorage.blob.core.windows.net"
        default_credential = "Ti4CfXXg/C274mrvnCl0ICnQsqSqokiHitO+lXgjg6oR3fssKlgirQ96wUXX7NHW2OSOkf7vl9hG+AStNqk6DA=="

        # Create the BlobServiceClient object
        blob_service_client = BlobServiceClient(account_url, credential=default_credential)

        container_client = blob_service_client.get_container_client(container="images")

        if container_client.exists():
            print("Container Exists")
        else:
            print("Not Exists")
            container_client.create_container()

        for f in (files):
            filename = "imageSample"+str(number_of_images)+".jpg"
            print(filename)
            file = secure_filename(f.filename)
            blob_client = container_client.upload_blob(name=filename,data=f)
            number_of_images += 1

            blob = blob_service_client.get_blob_client(container="images", blob=filename)
            with open(file=os.path.join(UPLOAD_FOLDER, filename), mode="wb") as sample_blob:
                download_stream = blob_client.download_blob()
                #blob_content=download_stream.readall().decode("utf-8")
                #print(f"Your content is: '{blob_content}'")
                sample_blob.write(download_stream.readall())


        
        return "AZURE BLOB"

if __name__ == "main":
    app.run()