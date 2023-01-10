from pydantic import BaseSettings


class Settings(BaseSettings):
    MODEL_NAME: str

    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_API_HOST: str
    MINIO_BUCKET_MODELS: str


settings = Settings()
