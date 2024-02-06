import os
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
    return_payload = {
        'current-time': pendulum.now().in_timezone('UTC').to_w3c_string(),
        'health-check': {
            'loading-config': os.getenv("CONFIGMAP_VARIABLE") if os.getenv("CONFIGMAP_VARIABLE") is not None else "fail",
            'loading-secrets': os.getenv("SECRETS_VARIABLE") if os.getenv("SECRETS_VARIABLE") is not None else "fail",
        },
    }

    return return_payload
