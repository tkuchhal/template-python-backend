import os
import pendulum
from fastapi import FastAPI
from loguru import logger
import dotenv
import requests

import sys

# Configure Loguru to log to stdout
logger.remove()
logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")

dotenv.load_dotenv()

app = FastAPI()

# Load environment variables once when the application starts
configmap_variable = os.getenv("CONFIGMAP_VARIABLE", "fail")
secrets_variable = os.getenv("SECRETS_VARIABLE", "fail")


@app.get('/')
@app.get('/health')
def get_health():
    try:
        return_payload = {
            'testing-github-actions': 'success',
            'current-time': pendulum.now().in_timezone('UTC').to_w3c_string(),
            'health-check': {
                'loading-config': configmap_variable,
                'loading-secrets': secrets_variable,
            },
        }
    except Exception as e:
        logger.error(f"An error occurred in get_health: {e}")
        return_payload = {'error': str(e)}

    return return_payload


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
