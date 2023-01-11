FROM python:3.7.16-slim

WORKDIR /app
COPY ./web/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY ./web /app/web
COPY ./utils /app/web/api/src