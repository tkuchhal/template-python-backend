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
@app.get('/health')
def get_health(response: Response):
    if os.getenv("CONFIGMAP_VARIABLE") is None or os.getenv("SECRETS_VARIABLE") is None:
        response.status_code = 500

    if os.getenv("DB_CONNECTION_URL") is None or os.getenv("DB_USER") is None or os.getenv("DB_PASSWORD") is None:
        response.status_code = 500

    os.environ["BUILD_TIME"] = pendulum.now().subtract(minutes=10).to_w3c_string()
    os.environ["DEPLOY_TIME"] = pendulum.now().subtract(minutes=40).to_w3c_string()

    return {
        'current-time': pendulum.now().in_timezone('UTC').to_w3c_string(),
        'image-metadata': {
            'build-time': pendulum.parse(os.getenv('BUILD_TIME')).diff_for_humans() + f" ({pendulum.parse(os.getenv('BUILD_TIME')).in_timezone('UTC')})",
            'deploy-time': pendulum.parse(os.getenv('DEPLOY_TIME')).diff_for_humans() + f" ({pendulum.parse(os.getenv('DEPLOY_TIME')).in_timezone('UTC')})",
            'current-image': os.getenv('IMAGE_NAME'),
        },
        'health-check': {
            'loading-config': os.getenv("CONFIGMAP_VARIABLE") if os.getenv("CONFIGMAP_VARIABLE") is not None else "fail",
            'loading-secrets': os.getenv("SECRETS_VARIABLE") if os.getenv("SECRETS_VARIABLE") is not None else "fail",
        },
        'db-connection-check': {
            'db-connection-url': os.getenv("DB_CONNECTION_URL") if os.getenv("DB_CONNECTION_URL") is not None else "fail",
            'db-user': os.getenv("DB_USER") if os.getenv("DB_USER") is not None else "fail",
            'db-password': os.getenv("DB_PASSWORD") if os.getenv("DB_PASSWORD") is not None else "fail",
        },
    }
