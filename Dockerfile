FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_PRODUCTION=True
ENV APP_DB_PATH=/data

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-warn-script-location --no-cache-dir --user -r requirements.txt

COPY ./manage.py ./deployment_manager/ ./
COPY ./docker/entrypoint.sh /usr/local/bin

RUN mkdir -p ${APP_DB_PATH} && chmod +x /usr/local/bin/entrypoint.sh

VOLUME [ "/data" ]

ENTRYPOINT ["entrypoint.sh"]
