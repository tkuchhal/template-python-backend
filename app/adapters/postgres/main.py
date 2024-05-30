import os
from sqlmodel import SQLModel, create_engine, Session, select
from sqlalchemy.exc import SQLAlchemyError
from loguru import logger


class PostgresAdapter:
    _instance = None
    _engine = None
    _session = None
    _db_url = None

    def __new__(cls, db_url):
        if cls._instance is None:
            cls._instance = super(PostgresAdapter, cls).__new__(cls)
            cls._db_url = db_url
        return cls._instance

    @property
    def engine(self):
        if self._engine is None:
            if self._db_url is None:
                raise ValueError("DATABASE_URL environment variable not set")

            self._engine = create_engine(self._db_url)
            logger.info("Database engine created successfully")

        return self._engine

    def get_session(self) -> Session:
        return Session(self.engine)

    async def ping(self) -> (bool, str):
        try:
            with self.get_session() as session:
                session.exec(select(1)).first()
                return True, 'ok'
        except SQLAlchemyError as e:
            logger.error(f"Failed to ping PostgreSQL: {e}")
            return False, e
