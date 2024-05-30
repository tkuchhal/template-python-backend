from typing import Optional

from sqlmodel import SQLModel, Field
from ..adapters.postgres.main import PostgresAdapter


def run_migrations(db_instance: PostgresAdapter):
    SQLModel.metadata.create_all(db_instance.engine)


class TestTable(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
