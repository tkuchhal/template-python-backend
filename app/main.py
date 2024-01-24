import os
import requests
from fastapi import Response
import pendulum
from fastapi import FastAPI
from loguru import logger
import dotenv

import sys

# Configure Loguru to log to stdout
logger.remove()
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")

dotenv.load_dotenv()

app = FastAPI()


@app.get('/')
def get_index():
    return {'message': 'Hello, world!'}


@app.get('/health')
def get_health(response: Response):
    if os.getenv("CONFIGMAP_VARIABLE") is None or os.getenv("SECRETS_VARIABLE") is None:
        response.status_code = 500

    return {
        'time': pendulum.now().in_timezone('UTC').to_w3c_string(),
        'health-checks': {
            'loading-config': "success" if os.getenv("CONFIGMAP_VARIABLE") is not None else "fail",
            'loading-secrets': "success" if os.getenv("SECRETS_VARIABLE") is not None else "fail",
        }
    }
