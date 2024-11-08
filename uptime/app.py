from uptime.routes import router

from fastapi import FastAPI

app = FastAPI()
app.include_router(router, prefix="/api")
