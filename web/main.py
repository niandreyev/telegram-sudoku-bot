from fastapi import FastAPI

from web.api.routers import router

app = FastAPI()
app.include_router(router)
