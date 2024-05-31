import os

import pendulum
from fastapi import HTTPException
from loguru import logger

from app.config import ConfigManager

# Load environment variables once when the application starts
configmap_variable = os.getenv("CONFIGMAP_VARIABLE", "fail")
secrets_variable = os.getenv("SECRETS_VARIABLE", "fail")


async def get_health_status() -> dict:
    redis_adapter = ConfigManager.get_redis_adapter()
    redis_status, msg = await redis_adapter.ping() if redis_adapter else ("N/A", "Not configured")
    logger.info(f"Redis status: {redis_status}, {msg}")

    database_adapter = ConfigManager.get_postgres_adapter()
    database_status, msg = await database_adapter.ping() if database_adapter else ("N/A", "Not configured")
    logger.info(f"Database status: {database_status}, {msg}")

    mongodb_adapter = ConfigManager.get_mongodb_adapter()
    mongodb_status, msg = await mongodb_adapter.ping() if mongodb_adapter else ("N/A", "Not configured")
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
        logger.error("One or more services are not healthy", return_payload)
        raise Exception("One or more services are not healthy", return_payload)
    return return_payload
