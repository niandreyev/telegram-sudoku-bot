from datetime import datetime
from json import loads

from kafka import KafkaConsumer

from ocr import SudokuImagePipeline
from settings import settings

if __name__ == "__main__":

    image_pipeline = SudokuImagePipeline(
        minio_host=settings.MINIO_API_HOST,
        minio_access_key=settings.MINIO_ACCESS_KEY,
        minio_secret_key=settings.MINIO_SECRET_KEY,
        image_bucket_name=settings.MINIO_BUCKET_IMAGES,
        model_bucket_name=settings.MINIO_BUCKET_MODELS,
        model_object_name=settings.MODEL_NAME,
        model_file_path=settings.MODEL_NAME,
        kafka_bootstrap=settings.KAFKA_BOOTSTRAP,
        kafka_sudoku_topic=settings.KAFKA_SUDOKU_TOPIC,
        api_endpoint=settings.API_ENDPOINT,
    )

    consumer = KafkaConsumer(
        settings.KAFKA_IMAGES_TOPIC,
        bootstrap_servers=[settings.KAFKA_BOOTSTRAP],
        auto_offset_reset="earliest",
        group_id="image-consumer",
        value_deserializer=lambda x: loads(x.decode("utf-8")),
    )

    for message in consumer:
        print("Got message: {}, {}".format(message.value, datetime.now().strftime("%Y-%m-%d %H:%M")))
        image_pipeline.parse_image(**message.value)
