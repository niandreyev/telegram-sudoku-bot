FROM python:3.7.16-slim

WORKDIR /app
COPY ./sudoku_solver/requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt
RUN apt-get update && apt-get install tk-dev -y

COPY ./sudoku_solver /app
COPY ./utils /app
ENV PYTHONUNBUFFERED=1