FROM python:3.7.16-slim

WORKDIR /app
COPY ./message_waiter/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY ./message_waiter /app
ENV PYTHONUNBUFFERED=1