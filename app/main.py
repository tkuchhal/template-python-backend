import os
import pendulum
from fastapi import FastAPI, HTTPException
from .adapters.redis.main import RedisAdapter
from .adapters.postgres.main import PostgresAdapter
from .adapters.mongodb.main import MongoDBAdapter
from loguru import logger
import dotenv
import requests

import sys

# Configure Loguru to log to stdout
logger.remove()
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")

if os.getenv('ENVIRONMENT') != 'test':
    dotenv.load_dotenv()

db_instance = PostgresAdapter(db_url=os.getenv('DATABASE_URL'))
redis_instance = RedisAdapter(redis_url=os.getenv('REDIS_URL'))
mongodb_instance = MongoDBAdapter(mongodb_url=os.getenv('MONGO_URL'))

app = FastAPI()

# Load environment variables once when the application starts
configmap_variable = os.getenv("CONFIGMAP_VARIABLE", "fail")
secrets_variable = os.getenv("SECRETS_VARIABLE", "fail")


@app.get('/')
@app.get('/health')
async def get_health():
    try:
        redis_status, msg = await redis_instance.ping()
        logger.info(f"Redis status: {redis_status}, {msg}")

        database_status, msg = await db_instance.ping()
        logger.info(f"Database status: {database_status}, {msg}")

        mongodb_status, msg = await mongodb_instance.ping()
        logger.info(f"MongoDB status: {mongodb_status}, {msg}")

        return_payload = {
            'current-time': pendulum.now().in_timezone('UTC').to_w3c_string(),
            'build-time': os.getenv('BUILD_TIME', 'unknown'),
            'health-check': {
                'loading-config': configmap_variable,
                'loading-secrets': secrets_variable,
            },
            'infrastructure': {
                'redis': redis_status,
                'database': database_status,
                'mongodb': mongodb_status,
            },
            'status': 'ok' if all([redis_status, database_status, mongodb_status]) else 'error',
        }
        if return_payload.get('status') != 'ok':
            raise HTTPException(status_code=500, detail=return_payload)
        return return_payload

    except Exception as e:
        logger.error(f"An error occurred in get_health: {e}")
        return HTTPException(status_code=500, detail={'error': str(e)})


@app.get('/network')
def get_network():
    try:
        response = requests.get('https://httpbin.org/ip')
        response.raise_for_status()
        logger.info(f"Response from https://httpbin.org/ip: {response.json().get('origin')}")
        return {'outbound-ip': response.json().get('origin')}
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred in get_network: {e}")
        return {'error': str(e)}
