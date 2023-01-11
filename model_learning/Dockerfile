FROM python:3.7.16-slim

WORKDIR /app
COPY ./model_learning/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY ./model_learning /app
COPY ./utils /app