import os
import uuid

import azure.functions as func
import datetime
import json
import logging

from azure.cosmos import CosmosClient, exceptions, PartitionKey

app = func.FunctionApp()


@app.route(route="create_movie", methods=["POST"])
def create_movie(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid JSON body."}),
            mimetype="application/json",
            status_code=400
        )

    title = req_body.get('title')
    year = req_body.get('year')
    url_video = req_body.get('url_video')
    url_thumb = req_body.get('url_thumb')

    if not all([title, year, url_video, url_thumb]):
        return func.HttpResponse(
            json.dumps({"error": "Missing one or more required parameters: title, year, url_video, url_thumb."}),
            mimetype="application/json",
            status_code=400
        )

    movie = {
        'id': str(uuid.uuid4()),
        'title': title,
        'year': year,
        'url_video': url_video,
        'url_thumb': url_thumb,
        'created_at': datetime.datetime.now().isoformat()
    }

    try:
        cosmos_db_create(movie)
        return func.HttpResponse(
            json.dumps(movie),
            status_code=201,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error saving to Cosmos DB: {e}")
        return func.HttpResponse(
            json.dumps({"error": f"Internal Server Error: {e}"}),
            mimetype="application/json",
            status_code=500
        )


def cosmos_db_config():
    container_name = os.getenv("CONTAINER_NAME")

    client = CosmosClient(os.getenv("COSMOS_DB_ENDPOINT"), os.getenv("COSMOS_DB_KEY"))
    database = client.create_database_if_not_exists(id=os.getenv("DATABASE_NAME"))
    client = database.create_container_if_not_exists(
        id=container_name,
        partition_key=PartitionKey(path="/id"),
        offer_throughput=400
    )
    return client.get_container_client(container_name)


def cosmos_db_create(data):
    try:
        container = cosmos_db_config()
        container.create_item(body=data)
    except exceptions.CosmosHttpResponseError as e:
        return e
