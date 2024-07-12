### ConfigManager

A handy configmanager and set of adapters has been provided for Postgres, Redis and Celery. The ConfigManager
will automatically load the configuration from the environment variables and provide a connection to the
database or redis instance using the adapters. In addition, the ConfigManager for Postgres will automatically run
migrations on the database to bring it up to the latest version.

#### Connecting to the Database

    from app.config import ConfigManager
    from app.models import TestTable # Your model should inherit from SQLModel

    test_instance = TestTable(id=id, name=name)

    # Example insert query
    with db_instance.get_session() as session:
        session.add(test_instance)
        session.commit()

    # Example get (select) query by primary key
    with db_instance.get_session() as session:
        retrieved_instance = session.get(TestTable, id)
        logger.info(f"Retrieved instance: {retrieved_instance}")
        assert retrieved_instance.id == id
        assert retrieved_instance.name == name

#### Connecting to Redis

    from app.config import ConfigManager

    redis_instance = ConfigManager.get_redis_adapter()
    redis_instance.set(key, value)
    assert redis_instance.get(key) == value
    redis_instance.delete(key)
    assert redis_instance.get(key) is None

### Setting a new model

- Add your SQLModel to a file in the app/models directory
- Import your model in the app/models/__init__.py file
- Run the following command to generate the migration file

```bash
python ./migrations/gen_migration.py
```

- Once generated, you can apply the migration by running the following command

```bash
python ./migrations/migrate.py
```

- Alternatively, just using the ConfigManager to connect to the DB will automatically run the migrations at
  initialization!

### Testing

- A test container for Redis, Celery and Postgres is provided in the docker-compose.yml file. The test containers will
  also automatically get generated and injected when running the pytest tests, along with
  migrations. 