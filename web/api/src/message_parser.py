import io
from typing import Any, Dict

from httpx import AsyncClient
from pydantic import BaseSettings
from web.api.schemas.parsed_message import TGUpdateParsed

from .kafka_handler import KafkaHandler
from .minio_handler import MinioHandler


class TelegramAPIUpdateObjectParser:
    @staticmethod
    def _check_is_message_have_photo(message_dict: Dict[str, Any]) -> bool:
        """Проверка на то, что входящее сообщение содержит фото"""
        return "photo" in message_dict.keys()

    def __init__(self, client: AsyncClient, tg_api_url: str, tg_api_file_url: str):
        self.client = client
        self.tg_api_url = tg_api_url
        self.tg_api_file_url = tg_api_file_url

    async def parse_update_instance(self, update_json: Dict[str, Any]) -> TGUpdateParsed:
        """Парсим один объект Update, пытаемся вытащить изображение из сообщения"""
        message = update_json["message"]
        chat_id = message["chat"]["id"]
        has_photo = TelegramAPIUpdateObjectParser._check_is_message_have_photo(message)
        if has_photo:
            file_id = message["photo"][-1]["file_id"]
            file_meta_response = await self.client.get(f"{self.tg_api_url}/getFile", params={"file_id": file_id})
            if file_meta_response.status_code == 200:
                file_metadata = file_meta_response.json()["result"]
                file_path = file_metadata["file_path"]
                file_uuid = file_metadata["file_unique_id"]
                file_bytes_response = await self.client.get(f"{self.tg_api_file_url}/{file_path}")
                if file_bytes_response.status_code == 200:
                    file_minio_path = f"{file_uuid}.{file_path.split('.')[-1]}"
                    return TGUpdateParsed(
                        success=True,
                        chat_id=chat_id,
                        has_photo=has_photo,
                        file_id=file_id,
                        file_unique_id=file_uuid,
                        file_path=file_path,
                        file_minio_path=file_minio_path,
                        file_bytes=io.BytesIO(file_bytes_response.content),
                    )
                else:
                    return TGUpdateParsed(
                        success=False,
                        chat_id=chat_id,
                        has_photo=has_photo,
                        file_id=file_id,
                        file_unique_id=file_uuid,
                        file_path=file_path,
                        error_message="Unable to load file from TG server. Please try again later",
                    )
            else:
                return TGUpdateParsed(
                    success=False,
                    chat_id=chat_id,
                    has_photo=has_photo,
                    file_id=file_id,
                    error_message="File not found on TG file api. Please try again later",
                )
        else:
            return TGUpdateParsed(
                success=False,
                chat_id=chat_id,
                has_photo=has_photo,
                error_message="Photo not founded",
            )


class DoPipelineTelegramAPIObject:
    """
    1. Парсим сообщение
    2. Сохраняем изображение в Minio(если есть)
    3. Передаем сообщение в кафку для дальнейшей обработки
    """

    def __init__(self, client: AsyncClient, settings: BaseSettings) -> None:
        self.update_parser = TelegramAPIUpdateObjectParser(
            client=client,
            tg_api_url=f"{settings.TG_URL}/{settings.TG_TOKEN}",
            tg_api_file_url=f"{settings.TG_URL}/file/{settings.TG_TOKEN}",
        )
        self.minio_handler = MinioHandler(
            host=settings.MINIO_API_HOST, access_key=settings.MINIO_ACCESS_KEY, secret_key=settings.MINIO_SECRET_KEY
        )
        self.minio_bucket = settings.MINIO_BUCKET_IMAGES
        self.kafka_handler = KafkaHandler(kafka_bootstrap=settings.KAFKA_BOOTSTRAP, topic=settings.KAFKA_IMAGES_TOPIC)

    async def do_pipeline(self, update_instance: str) -> Dict:
        res = await self.update_parser.parse_update_instance(update_instance)
        if res.success:
            try:
                self.minio_handler.save_in_bucket(self.minio_bucket, res.file_minio_path, res.file_bytes)
            except Exception as err:
                print(err)
                return {"chat_id": res.chat_id, "parse_status": False, "parse_msg": "Service broken. Minio write error"}
            else:
                try:
                    self.kafka_handler.send_message_to_topic(res.json_to_kafka())
                except Exception as err:
                    print(err)
                    return {
                        "chat_id": res.chat_id,
                        "parse_status": False,
                        "parse_msg": "Service broken. Kafka write error",
                    }
                else:
                    return {"chat_id": res.chat_id, "parse_status": True, "parse_msg": "Success got image"}
        else:
            return {"chat_id": res.chat_id, "parse_status": False, "parse_msg": res.error_message}
