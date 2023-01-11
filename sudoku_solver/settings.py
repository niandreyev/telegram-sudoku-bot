from pydantic import BaseSettings


class Settings(BaseSettings):
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_API_HOST: str
    MINIO_BUCKET_SOLVED: str

    KAFKA_BOOTSTRAP: str
    KAFKA_SUDOKU_TOPIC: str

    API_ENDPOINT: str
    API_FILE_ENDPOINT: str


settings = Settings()
