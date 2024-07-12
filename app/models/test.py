from typing import Optional

from sqlmodel import SQLModel, Field


class TestTable(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
