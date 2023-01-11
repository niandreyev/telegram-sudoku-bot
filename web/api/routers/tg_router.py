from fastapi import APIRouter
from httpx import AsyncClient, Timeout
from web.api.src.message_parser import DoPipelineTelegramAPIObject
from web.api.src.minio_handler import MinioHandler
from web.settings import settings

router = APIRouter()


@router.get("/send_sudoku")
async def send_sudoku(chat_id: str, object_id: str):
    TG_API_URL = f"{settings.TG_URL}/{settings.TG_TOKEN}"
    minio_client = MinioHandler(
        host=settings.MINIO_API_HOST, access_key=settings.MINIO_ACCESS_KEY, secret_key=settings.MINIO_SECRET_KEY
    )
    async with AsyncClient(timeout=Timeout(settings.TG_API_TIMEOUT, read=None)) as client:
        image = minio_client.load_file_in_memory(settings.MINIO_BUCKET_SOLVED, object_id)
        await client.post(f"{TG_API_URL}/sendPhoto", params={"chat_id": chat_id}, files={"photo": image})


@router.get("/send_text")
async def send_sudoku(chat_id: str, text: str):
    TG_API_URL = f"{settings.TG_URL}/{settings.TG_TOKEN}"
    async with AsyncClient(timeout=Timeout(settings.TG_API_TIMEOUT, read=None)) as client:
        await client.post(f"{TG_API_URL}/sendMessage", params={"chat_id": chat_id, "text": text})


@router.get("/parse_last_message")
async def parse_last_message():
    TG_API_URL = f"{settings.TG_URL}/{settings.TG_TOKEN}"

    async with AsyncClient(timeout=Timeout(settings.TG_API_TIMEOUT, read=None)) as client:
        updates_response = await client.get(url=f"{TG_API_URL}/getUpdates")
        if updates_response.status_code == 200:
            updates = updates_response.json()
            if len(updates["result"]) > 0:
                last_update = updates["result"][-1]
                pipeline = DoPipelineTelegramAPIObject(client, settings)
                status = await pipeline.do_pipeline(last_update)
            else:
                status = {"chat_id": None, "parse_status": False, "parse_msg": "No updates founded."}
        else:
            status = {
                "chat_id": None,
                "parse_status": False,
                "parse_msg": f"No updates. Got status_code - {updates_response.status_code }",
            }

        if status["chat_id"]:
            msg_params = {"chat_id": status["chat_id"], "text": status["parse_msg"]}
            updates_response = await client.post(url=f"{TG_API_URL}/sendMessage", params=msg_params)
            if updates_response.status_code == 200:
                status["response_user"] = True
            else:
                status["response_user"] = False
        else:
            status["response_user"] = None
        return status
