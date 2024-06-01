import os
import sys
import time
from alembic.config import Config
from alembic import command
from alembic.migration import MigrationContext
from alembic.autogenerate import compare_metadata
from sqlalchemy import create_engine, text
from sqlmodel import SQLModel
from testcontainers.core.container import DockerContainer

# Ensure the app package can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def start_postgres_container():
    container = DockerContainer("postgres:latest")
    container.with_env("POSTGRES_USER", "test")
    container.with_env("POSTGRES_PASSWORD", "test")
    container.with_env("POSTGRES_DB", "test_db")
    container.with_exposed_ports(5432)
    container.start()

    # Wait for PostgreSQL to become ready
    timeout = 30  # seconds
    start_time = time.time()

    while True:
        try:
            connection_url = f"postgresql://test:test@{container.get_container_host_ip()}:{container.get_exposed_port(5432)}/test_db"
            # Attempt to connect to the PostgreSQL server to verify it is ready
            engine = create_engine(connection_url)
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            break
        except Exception as e:
            if time.time() - start_time > timeout:
                container.stop()
                raise TimeoutError(f"PostgreSQL container did not become ready in {timeout} seconds.") from e
            time.sleep(1)

    return container, connection_url


def generate_migrations():
    container, postgres_url = start_postgres_container()

    try:
        # Apply existing migrations to the test database
        alembic_cfg = Config(os.path.join(os.path.dirname(__file__), 'alembic.ini'))
        alembic_cfg.set_main_option('sqlalchemy.url', postgres_url)
        command.upgrade(alembic_cfg, "head")

        # Ensure models are imported
        import app.models  # Make sure this import is here to load all models

        # Check for changes
        engine = create_engine(postgres_url)
        with engine.connect() as connection:
            context = MigrationContext.configure(connection)
            diff = compare_metadata(context, SQLModel.metadata)

        if not diff:
            print("No changes detected, skipping migration generation.")
            return

        # Ensure the migrations/versions folder exists
        versions_dir = os.path.join(os.path.dirname(__file__), 'versions')
        os.makedirs(versions_dir, exist_ok=True)

        # Generate new migrations
        command.revision(alembic_cfg, message="Auto-generated migration", autogenerate=True)
    finally:
        # Stop the container
        container.stop()


if __name__ == "__main__":
    generate_migrations()
