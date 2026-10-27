from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config import Settings

settings = Settings.from_env()
app = FastAPI(title="Lecture Cheat Sheet API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=[settings.frontend_origin],
                   allow_methods=["GET", "POST"], allow_headers=["Content-Type"])
app.include_router(router)
