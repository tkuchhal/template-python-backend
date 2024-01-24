# 
FROM python:3.11-alpine

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install --no-cache-dir uvicorn


# The following RUN command does the following:
# 1. Checks if BUILD_TIME already exists in .env and replaces it, or appends it if it doesn't exist.
# 2. Checks if the directory is a Git repository with no unstaged changes and writes the SHA ID or "undefined".
RUN if [ -f .env ]; then \
        sed -i '/^BUILD_TIME=/d' .env; \
    fi; \
    echo "BUILD_TIME=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" >> .env; \
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1 && [ -z "$(git status --porcelain)" ]; then \
        SHA_ID=$(git rev-parse HEAD); \
    else \
        SHA_ID="undefined"; \
    fi; \
    echo "GIT_SHA_ID=$SHA_ID" >> .env


# 
COPY ./app /code/app
COPY ./tests /code/tests
RUN ["date -u +"%Y-%m-%dT%H:%M:%SZ" "

# 
CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8080"]

EXPOSE 8080/tcp