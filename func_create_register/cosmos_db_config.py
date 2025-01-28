import os

from azure.cosmos import CosmosClient, exceptions, PartitionKey


async def cosmos_db_config():
    container_name = os.getenv("CONTAINER_NAME")

    client = CosmosClient(os.getenv("COSMOS_DB_ENDPOINT"), os.getenv("COSMOS_DB_KEY"))
    database = client.create_database_if_not_exists(id=os.getenv("DATABASE_NAME"))
    client = database.create_container_if_not_exists(
        id=container_name,
        partition_key=PartitionKey(path="/id"),
        offer_throughput=400
    )
    return client.get_container_client(container_name)


async def cosmos_db_create(data):
    try:
        container = await cosmos_db_config()
        container.create_item(body=data)
    except exceptions.CosmosHttpResponseError as e:
        return e
