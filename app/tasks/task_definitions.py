# app/task_definitions.py
from app.tasks.celery_config import celery


@celery.task
def add(arg1: int, arg2: int) -> int:
    return arg1 + arg2
