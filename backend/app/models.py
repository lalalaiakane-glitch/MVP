"""資料模型：ContentChunk（證據分級內容）與 EvalQuestion（評估測試題）。"""
from datetime import datetime, date

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean
from pydantic import BaseModel
from typing import Optional

from app.db import Base


class ContentChunk(Base):
    """一條品牌內容，標記證據等級與來源。"""
    __tablename__ = "content_chunks"

    id = Column(Integer, primary_key=True, index=True)
    brand_id = Column(String, nullable=False, default="demo-brand")
    product_id = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    # A = 臨床/研究等級證據；B = 官方仿單/成分事實；C = 使用者回饋/軼事；D = 未經查證
    evidence_tier = Column(String, nullable=False)
    # efficacy_claim（療效聲明）/ ingredient_fact（成分事實）/ anecdotal（軼事）/ usage_instruction（使用方式）
    claim_type = Column(String, nullable=False)
    source_citation = Column(String, nullable=True)
    last_reviewed_at = Column(Date, nullable=True, default=date.today)
    created_at = Column(DateTime, default=datetime.utcnow)


class EvalQuestion(Base):
    """評估用測試問題。"""
    __tablename__ = "eval_questions"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    product_id = Column(String, nullable=True)
    expected_intent = Column(String, nullable=True)
    expect_blocked = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)


# ---- Pydantic schemas（API 輸入輸出用） ----

class ContentChunkIn(BaseModel):
    brand_id: str = "demo-brand"
    product_id: str
    text: str
    evidence_tier: str
    claim_type: str
    source_citation: Optional[str] = None


class ContentChunkOut(ContentChunkIn):
    id: int

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    question: str
    product_id: Optional[str] = None


class EvalQuestionIn(BaseModel):
    question: str
    product_id: Optional[str] = None
    expected_intent: Optional[str] = None
    expect_blocked: bool = False
    notes: Optional[str] = None
