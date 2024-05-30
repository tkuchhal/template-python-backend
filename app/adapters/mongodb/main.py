import os
import dotenv
from loguru import logger
from pymongo import MongoClient, errors

dotenv.load_dotenv()


class MongoDBAdapter:
    _instance = None
    _mongodb_url = None

    def __new__(cls, mongodb_url):
        if cls._instance is None:
            cls._instance = super(MongoDBAdapter, cls).__new__(cls)
            cls._instance._connection = None
            cls._instance._db = None
            cls._mongodb_url = mongodb_url
        return cls._instance

    @property
    def connection(self):
        if self._connection is None:
            if self._mongodb_url is None:
                raise ValueError("MONGO_URL environment variable not set")

            try:
                self._connection = MongoClient(
                    self._mongodb_url,
                    serverSelectionTimeoutMS=int(os.getenv('MONGO_MAX_TIMEOUT', 2000)),  # Default timeout is 2000ms
                    maxPoolSize=int(os.getenv('MONGO_MAX_POOL_SIZE', 100)),  # Default max pool size is 100
                    minPoolSize=int(os.getenv('MONGO_MIN_POOL_SIZE', 0))  # Default min pool size is 0
                )
                self._db = self._connection.get_database(os.getenv('MONGO_DB', 'default'))
            except errors.ConnectionFailure as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise

        return self._connection

    @property
    def db(self):
        if self._db is None:
            self.connection  # Ensure the connection and db are initialized
        return self._db

    async def ping(self) -> (bool, str):
        try:
            value = self.connection.admin.command('ping')
            return value is not None, value
        except errors.PyMongoError as e:
            logger.error(f"Failed to ping MongoDB: {e}")
            return False, e

    def get_collection(self, collection_name):
        try:
            return self.db[collection_name]
        except errors.PyMongoError as e:
            logger.error(f"Failed to get collection {collection_name}: {e}")
            return None

    def find_one(self, collection_name, query):
        try:
            collection = self.get_collection(collection_name)
            if collection is not None:
                return collection.find_one(query)
        except errors.PyMongoError as e:
            logger.error(f"Failed to find one in collection {collection_name} with query {query}: {e}")
        return None

    def insert_one(self, collection_name, document):
        try:
            collection = self.get_collection(collection_name)
            if collection is not None:
                return collection.insert_one(document)
        except errors.PyMongoError as e:
            logger.error(f"Failed to insert document into collection {collection_name}: {e}")
        return None

    def delete_one(self, collection_name, query):
        try:
            collection = self.get_collection(collection_name)
            if collection is not None:
                return collection.delete_one(query)
        except errors.PyMongoError as e:
            logger.error(f"Failed to delete document from collection {collection_name} with query {query}: {e}")
        return None

    def search(self, collection_name, query, projection=None, limit=0):
        try:
            collection = self.get_collection(collection_name)
            if collection is not None:
                return list(collection.find(query, projection).limit(limit))
        except errors.PyMongoError as e:
            logger.error(f"Failed to search in collection {collection_name} with query {query}: {e}")
        return []
