# FastAPI Project Template

This project is a comprehensive template for building scalable web applications using FastAPI, with integrated support for PostgreSQL, Redis, MongoDB, and Celery. It provides a solid foundation for developing robust backend services with good practices for configuration management, database interactions, background task processing, and testing.

## Features

- FastAPI web framework
- PostgreSQL database with SQLModel ORM
- Redis for caching and message broker
- MongoDB for document storage
- Celery for background task processing
- Docker and docker-compose for easy development and deployment
- Comprehensive testing setup with pytest and Docker containers
- Wiremock for mocking external API calls in tests
- Custom ConfigManager for centralized configuration and adapter management

## Project Structure

```
.
├── app
│   ├── adapters
│   │   ├── mongodb
│   │   ├── postgres
│   │   └── redis
│   ├── models
│   ├── tasks
│   │   ├── celery_config.py
│   │   └── task_definitions.py
│   ├── config.py
│   └── main.py
├── tests
│   ├── conftest.py
│   └── test_main.py
├── migrations
│   ├── gen_migration.py
│   └── migrate.py
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. Create a `.env` file in the root directory and add the necessary environment variables:
   ```
   DATABASE_URL=postgresql+psycopg2://postgres:postgres@postgres:5432/test_db
   REDIS_URL=redis://redis:6379
   MONGO_URL=mongodb://mongodb:27017/
   MONGO_DB=test_db
   ```

3. Build and run the Docker containers:
   ```
   docker-compose up --build
   ```

## Usage

### ConfigManager

The `ConfigManager` provides a centralized way to manage connections to PostgreSQL, Redis, and MongoDB. It automatically loads configuration from environment variables and manages database connections.

#### Connecting to the Database

```python
from app.config import ConfigManager
from app.models import TestTable

db_instance = ConfigManager.get_postgres_adapter()

# Example insert query
with db_instance.get_session() as session:
    test_instance = TestTable(id=1, name="Test")
    session.add(test_instance)
    session.commit()

# Example select query
with db_instance.get_session() as session:
    retrieved_instance = session.get(TestTable, 1)
    print(f"Retrieved instance: {retrieved_instance}")
```

#### Connecting to Redis

```python
from app.config import ConfigManager

redis_instance = ConfigManager.get_redis_adapter()
redis_instance.set("key", "value")
assert redis_instance.get("key") == "value"
```

### Creating a New Model

1. Add your SQLModel to a file in the `app/models` directory
2. Import your model in `app/models/__init__.py`
3. Generate a migration file:
   ```
   python ./migrations/gen_migration.py
   ```
4. Apply the migration:
   ```
   python ./migrations/migrate.py
   ```

Note: Using the ConfigManager to connect to the database will automatically run migrations on initialization.

### Creating Celery Tasks

1. Define your task in `app/tasks/task_definitions.py`:
   ```python
   from app.tasks.celery_config import celery

   @celery.task
   def your_task(arg1, arg2):
       # Task logic here
       return result
   ```

2. Use the task in your application:
   ```python
   from app.tasks.task_definitions import your_task

   result = your_task.delay(arg1, arg2)
   ```

## Testing

Run tests using pytest:

```
pytest
```

The test setup uses Docker containers for PostgreSQL, Redis, MongoDB, and Wiremock, ensuring isolated and consistent test environments.

## Deployment

1. Ensure all necessary environment variables are set in your production environment.
2. Build the Docker image:
   ```
   docker build -t your-app-name .
   ```
3. Run the container:
   ```
   docker run -p 80:80 your-app-name
   ```
