import os

from fastapi import FastAPI
from loguru import logger
import requests

import sys

from .config import ConfigManager
from app.api.routes import router as api_router

# Configure Loguru to log to stdout
logger.remove()
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")

ConfigManager.initialize()
app = FastAPI()
app.include_router(api_router)


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


@app.get('/random')
def get_random():
    try:
        random_uuid_base_url = os.getenv('RANDOM_UUID_BASE_URL') if os.getenv('RANDOM_UUID_BASE_URL') else 'https://httpbin.org'
        response = requests.get(random_uuid_base_url + '/uuid')
        response.raise_for_status()
        logger.info(f"Response from {random_uuid_base_url} generator: {response.json().get('uuid')}")
        return {'uuid': response.json().get('uuid')}
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred in get_random: {e}")
        return {'error': str(e)}
