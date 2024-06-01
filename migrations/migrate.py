import os
import sys
import dotenv
from alembic.config import Config
from alembic import command, script
from sqlalchemy import create_engine, text
from alembic.runtime.migration import MigrationContext

if os.getenv('DATABASE_URL') is None:
    dotenv.load_dotenv()  # Load environment variables from .env file

# Ensure the app package can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_current_revision(alembic_cfg):
    script_dir = script.ScriptDirectory.from_config(alembic_cfg)
    head_revision = script_dir.get_current_head()
    return head_revision


def get_applied_revisions(alembic_cfg):
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("The DATABASE_URL environment variable is not set.")

    engine = create_engine(db_url)
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        applied_revisions = context.get_current_heads()

    return [rev for rev in applied_revisions]


def run_migrations():
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise ValueError("The DATABASE_URL environment variable is not set.")

    alembic_cfg = Config(os.path.join(os.path.dirname(__file__), 'alembic.ini'))
    alembic_cfg.set_main_option('sqlalchemy.url', db_url)

    current_revision = get_current_revision(alembic_cfg)
    applied_revisions = get_applied_revisions(alembic_cfg)

    if current_revision not in applied_revisions:
        print("New migrations found. Applying migrations...")
        command.upgrade(alembic_cfg, "head")
        print("Migrations applied successfully.")
    else:
        print("No new migrations to apply.")


if __name__ == "__main__":
    run_migrations()
