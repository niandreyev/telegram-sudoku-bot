from pydantic import BaseSettings


class Settings(BaseSettings):
    TG_URL: str
    TG_TOKEN: str
    TG_API_TIMEOUT: int

    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_API_HOST: str
    MINIO_BUCKET_IMAGES: str
    MINIO_BUCKET_SOLVED: str

    KAFKA_BOOTSTRAP: str
    KAFKA_IMAGES_TOPIC: str


settings = Settings()
