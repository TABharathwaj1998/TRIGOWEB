from flask import Flask, render_template
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient


app = Flask(__name__)

@app.route("/")
def home():
    account_url = "https://tabsamplestorage.blob.core.windows.net"
    default_credential = "Ti4CfXXg/C274mrvnCl0ICnQsqSqokiHitO+lXgjg6oR3fssKlgirQ96wUXX7NHW2OSOkf7vl9hG+AStNqk6DA=="

    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient(account_url, credential=default_credential)
    container_client = blob_service_client.create_container("imagefolder")
    return "AZURE BLOB"

if __name__ == "main":
    app.run()