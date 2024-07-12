from sqlmodel import SQLModel
from app.adapters.postgres.main import PostgresAdapter


def run_migrations(db_instance: PostgresAdapter):
    SQLModel.metadata.create_all(db_instance.engine)
