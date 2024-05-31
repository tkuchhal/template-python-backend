import random

from fastapi import APIRouter, HTTPException
from app.core.main import get_health_status
from loguru import logger

router = APIRouter()


@router.get('/')
@router.get('/health')
async def health_check():
    try:
        logger.info("Health check")
        health_status = await get_health_status()
        return health_status
    except Exception as e:
        logger.error(f"An error occurred in health_check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/tasks/test')
async def test_task():
    from app.tasks import task_definitions
    logger.info("Testing task")
    job = task_definitions.add.delay(random.randint(1, 1000), random.randint(1, 1000))
    return {'task_id': job.id, 'task_status': job.status}
