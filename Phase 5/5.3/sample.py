from flask import Flask, render_template, request
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
from werkzeug.utils import secure_filename


app = Flask(__name__,template_folder="template")

@app.route('/')
def home():
    return render_template("upload.html")

@app.route("/azureUpload", methods=["POST","GET"])
def azureUpload():
    if request.method == "POST":
        files = request.files.getlist("filename[]")
        print(files[1])
        account_url = "https://tabsamplestorage.blob.core.windows.net"
        default_credential = "Ti4CfXXg/C274mrvnCl0ICnQsqSqokiHitO+lXgjg6oR3fssKlgirQ96wUXX7NHW2OSOkf7vl9hG+AStNqk6DA=="

        # Create the BlobServiceClient object
        blob_service_client = BlobServiceClient(account_url, credential=default_credential)
        container_client = blob_service_client.create_container("imagefolder")

        blob_client = container_client.upload_blob(name='imageSample',data=files[1])

        '''for f in files:
            file = secure_filename(f.filename)
            blob_client = container_client.upload_blob()'''
        
        return "AZURE BLOB"

if __name__ == "main":
    app.run()