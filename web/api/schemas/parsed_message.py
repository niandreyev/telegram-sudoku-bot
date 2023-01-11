from typing import Any, Optional

from pydantic import BaseModel, Field


class TGUpdateParsed(BaseModel):
    """Класс TGUpdateParsed

    Описывает формат результата парсинга объекта Update из TG API
    """

    success: bool = Field(None, title="Результат, нашли ли фотку в сообщении")
    chat_id: int = Field(None, title="Id чата откуда пришло сообщение")
    has_photo: bool = Field(None, title="Есть ли фото в сообщении")
    file_unique_id: Optional[str] = Field(None, title="Краткий ID файла на сервере телеграмма")
    file_path: Optional[str] = Field(None, title="Путь к файлу на сервере телеграмма")
    file_minio_path: Optional[str] = Field(None, title="Путь к файлу в MINIO")
    file_bytes: Optional[Any] = Field(None, title="Изображение")
    error_message: Optional[str] = Field(None, title="Сообщение в случае ошибки")

    def json_to_logger(self):
        return self.json(exclude={"file_bytes"})

    def json_to_kafka(self):
        return self.json(include={"chat_id", "file_minio_path"})
