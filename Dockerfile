# 
FROM python:3.11-alpine
RUN apk add --no-cache bash curl

# 
WORKDIR /code

# 
COPY ./requirements.txt /code/requirements.txt

# 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
RUN pip install --no-cache-dir pytest
RUN pip install --no-cache-dir uvicorn

RUN if grep -q 'BUILD_TIME=' /code/.env; then \
        sed -i "/BUILD_TIME=/c\BUILD_TIME=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" /code/.env; \
    else \
        echo "BUILD_TIME=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" >> /code/.env; \
    fi


# 
COPY ./app /code/app
COPY ./tests /code/tests

# 
CMD ["uvicorn", "app.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]

EXPOSE 80/tcp