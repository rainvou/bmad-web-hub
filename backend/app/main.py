from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.services.skill_catalog import skill_catalog
from app.routes import skills, sessions, outputs, ws


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await skill_catalog.scan()
    yield


app = FastAPI(title="BMAD Web Hub", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(skills.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(outputs.router, prefix="/api")
app.include_router(ws.router)
