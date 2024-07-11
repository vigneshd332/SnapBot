import os

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection


def load_database(collection_name: str) -> AsyncIOMotorCollection:
    """Loads the MongoDB database and returns the collection from that database. If the collection name specified is not found in the database, It will be created with that name instead."""

    cluster = AsyncIOMotorClient(os.getenv("MONGODB_CONNECTION_STRING"))
    database = cluster.get_database("SnapBot_Database")
    return database.get_collection(collection_name)
