import os
from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Field
import dotenv
from loguru import logger
from typing import Optional

dotenv.load_dotenv()


class PostgresAdapter:
    _instance = None
    _engine = None
    _session = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PostgresAdapter, cls).__new__(cls)
        return cls._instance

    @property
    def engine(self):
        if self._engine is None:
            db_url = os.getenv('DATABASE_URL')
            if db_url is None:
                raise ValueError("DATABASE_URL environment variable not set")

            self._engine = create_engine(db_url)
            logger.info("Database engine created successfully")

        return self._engine

    def get_session(self) -> Session:
        return Session(self.engine)

    def ping(self) -> bool:
        try:
            with self.get_session() as session:
                session.exec(select(1)).first()
                return True
        except SQLAlchemyError as e:
            logger.error(f"Failed to ping PostgreSQL: {e}")
            return False


# Usage example
if __name__ == "__main__":
    adapter = PostgresAdapter()


    class TestTable(SQLModel, table=True):
        id: Optional[int] = Field(default=None, primary_key=True)
        name: str


    SQLModel.metadata.create_all(adapter.engine)

    # Ping PostgreSQL server
    if adapter.ping():
        logger.info("PostgreSQL server is alive.")
    else:
        logger.error("Failed to connect to PostgreSQL server.")

    # Example add (insert) query
    test_instance = TestTable(id=1, name="test_name")
    with adapter.get_session() as session:
        session.add(test_instance)
        session.commit()

    # Example get (select) query by primary key
    with adapter.get_session() as session:
        retrieved_instance = session.get(TestTable, 1)
        logger.info(f"Retrieved instance: {retrieved_instance}")

    # Example query with filters
    with adapter.get_session() as session:
        statement = select(TestTable).where(TestTable.name == "test_name")
        result = session.exec(statement).all()
        logger.info(f"Query result: {result}")

    # Example delete query
    with adapter.get_session() as session:
        if retrieved_instance:
            session.delete(retrieved_instance)
            session.commit()
            logger.info(f"Deleted instance with id: {retrieved_instance.id}")
