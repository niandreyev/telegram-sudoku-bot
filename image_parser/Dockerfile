FROM python:3.7.16-slim

WORKDIR /app
COPY ./image_parser/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

COPY ./image_parser /app
COPY ./utils /app
ENV PYTHONUNBUFFERED=1