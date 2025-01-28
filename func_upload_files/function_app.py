import json
import os

import azure.functions as func
import datetime
import logging

from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

app = func.FunctionApp()


@app.route(route="upload_file", methods=["POST"])
def upload_file(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if not req.files:
        return func.HttpResponse(
            json.dumps({"error": "The request does not contain a file."}),
            mimetype="application/json",
            status_code=400
        )

    if 'file-type' not in req.headers:
        return func.HttpResponse(
            json.dumps({"error": "The request does not contain a file-type header."}),
            mimetype="application/json",
            status_code=400
        )

    file = req.files['file']

    file_type = req.headers['file-type']
    if file_type not in ['image', 'video']:
        return func.HttpResponse(
            json.dumps({"error": "The file-type header must be 'image' or 'video'."}),
            mimetype="application/json",
            status_code=400
        )

    try:
        connect_str = os.getenv("BLOB_STORAGE_CONNECT_STRING")
        container_name = f"{os.getenv('BLOB_STORAGE_CONTAINER_NAME')}/{file_type}"
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)

        file_name = f"{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}-{file.filename}"
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=file_name
        )

        blob_client.upload_blob(file, overwrite=True)
        blob_service_client.close()

        return func.HttpResponse(
            json.dumps({"message": f"File uploaded successfully to BlobStorage: {blob_service_client.url}"}),
            mimetype="application/json",
            status_code=200
        )
    except Exception as e:
        func.HttpResponse(
            json.dumps({"error": f"Error in upload file to BlobStorage: {e}"}),
            mimetype="application/json",
            status_code=500
        )
