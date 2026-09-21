"""內容管理 CRUD API。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import ContentChunk, ContentChunkIn, ContentChunkOut

router = APIRouter(prefix="/api/content", tags=["content"])


@router.get("", response_model=list[ContentChunkOut])
def list_content(db: Session = Depends(get_db)):
    return db.query(ContentChunk).order_by(ContentChunk.id.desc()).all()


@router.post("", response_model=ContentChunkOut)
def create_content(payload: ContentChunkIn, db: Session = Depends(get_db)):
    chunk = ContentChunk(**payload.model_dump())
    db.add(chunk)
    db.commit()
    db.refresh(chunk)
    return chunk


@router.put("/{content_id}", response_model=ContentChunkOut)
def update_content(content_id: int, payload: ContentChunkIn, db: Session = Depends(get_db)):
    chunk = db.query(ContentChunk).get(content_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="找不到這條內容")
    for k, v in payload.model_dump().items():
        setattr(chunk, k, v)
    db.commit()
    db.refresh(chunk)
    return chunk


@router.delete("/{content_id}")
def delete_content(content_id: int, db: Session = Depends(get_db)):
    chunk = db.query(ContentChunk).get(content_id)
    if not chunk:
        raise HTTPException(status_code=404, detail="找不到這條內容")
    db.delete(chunk)
    db.commit()
    return {"ok": True}
