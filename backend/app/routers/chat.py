"""問答測試 API：跑一次完整 pipeline，回傳完整 trace。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ChatRequest
from app.pipeline import run

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("")
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    result = run(db, question=payload.question, product_id=payload.product_id)
    return result
