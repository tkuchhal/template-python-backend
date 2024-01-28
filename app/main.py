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
    return {"message": "OK"}


@app.get('/health')
def get_health(response: Response):
    if os.getenv("CONFIGMAP_VARIABLE") is None or os.getenv("SECRETS_VARIABLE") is None:
        response.status_code = 500

    return {
        'current-time': pendulum.now().in_timezone('UTC').to_w3c_string(),
        'build-time': os.getenv('BUILD_TIME'),
        'deploy-time': os.getenv('DEPLOY_TIME'),
        'git-sha': os.getenv('GIT_SHA'),
        'health-check': {
            'loading-config': os.getenv("CONFIGMAP_VARIABLE") if os.getenv("CONFIGMAP_VARIABLE") is not None else "fail",
            'loading-secrets': os.getenv("SECRETS_VARIABLE") if os.getenv("SECRETS_VARIABLE") is not None else "fail",
        }
    }
