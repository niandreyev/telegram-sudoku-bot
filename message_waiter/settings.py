from pydantic import BaseSettings


class Settings(BaseSettings):
    TG_TOKEN: str
    API_TIMEOUT: int
    API_URL: str


settings = Settings()
