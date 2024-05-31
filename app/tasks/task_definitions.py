# app/task_definitions.py
from loguru import logger

from app.tasks.celery_config import celery


@celery.task
def add(arg1: int, arg2: int) -> int:
    result = arg1 + arg2
    logger.info(f"Adding {arg1} and {arg2} = {result}")
    return result
