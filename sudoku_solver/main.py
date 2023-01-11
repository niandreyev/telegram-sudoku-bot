from datetime import datetime
from json import loads

from kafka import KafkaConsumer

from settings import settings
from solver import SudokuSolvePipeline

if __name__ == "__main__":

    solve_pipeline = SudokuSolvePipeline(
        minio_host=settings.MINIO_API_HOST,
        minio_access_key=settings.MINIO_ACCESS_KEY,
        minio_secret_key=settings.MINIO_SECRET_KEY,
        solve_bucket_name=settings.MINIO_BUCKET_SOLVED,
        api_endpoint=settings.API_ENDPOINT,
        api_file_endpoint=settings.API_FILE_ENDPOINT,
    )

    consumer = KafkaConsumer(
        settings.KAFKA_SUDOKU_TOPIC,
        bootstrap_servers=[settings.KAFKA_BOOTSTRAP],
        auto_offset_reset="earliest",
        group_id="sudoku-solver",
        value_deserializer=lambda x: loads(x.decode("utf-8")),
    )

    for message in consumer:
        print("Got message: {}, {}".format(message.value, datetime.now().strftime("%Y-%m-%d %H:%M")))
        solve_pipeline.do_pipeline(**message.value)
