"""FastAPI 進入點。"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import Base, engine
from app.routers import content, chat, eval as eval_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="品牌 AI 客服證據守門系統 - MVP")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MVP 先全開，正式上線再收斂
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(content.router)
app.include_router(chat.router)
app.include_router(eval_router.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
