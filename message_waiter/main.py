from httpx import AsyncClient, Timeout
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler

from settings import settings


async def message_func(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with AsyncClient(timeout=Timeout(settings.API_TIMEOUT, read=None)) as client:
        await client.post(settings.API_URL, data=update.to_json())


if __name__ == "__main__":
    application = ApplicationBuilder().token(settings.TG_TOKEN).build()
    message_handler = MessageHandler(None, message_func)
    application.add_handler(message_handler)

    application.run_polling()
