from pydantic import BaseSettings


class Settings(BaseSettings):
    MODEL_NAME: str

    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_API_HOST: str
    MINIO_BUCKET_IMAGES: str
    MINIO_BUCKET_MODELS: str

    KAFKA_BOOTSTRAP: str
    KAFKA_IMAGES_TOPIC: str
    KAFKA_SUDOKU_TOPIC: str

    API_ENDPOINT: str


settings = Settings()
