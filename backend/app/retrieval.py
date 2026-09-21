"""TF-IDF 檢索 + 證據等級過濾。

MVP 刻意不用 embedding/向量資料庫，先驗證「檢索時依證據等級過濾」這個邏輯
本身有沒有用；之後要正式上線，把 _vectorize 換成真的 embedding 模型即可，
呼叫端的介面不用變。
"""
from dataclasses import dataclass
from typing import List, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from app.models import ContentChunk

# 數字越小代表證據等級越強
TIER_RANK = {"A": 1, "B": 2, "C": 3, "D": 4}


@dataclass
class RetrievedChunk:
    id: int
    text: str
    evidence_tier: str
    claim_type: str
    source_citation: Optional[str]
    score: float


def search(
    db: Session,
    question: str,
    min_evidence_tier: str,
    product_id: Optional[str] = None,
    top_k: int = 3,
) -> List[RetrievedChunk]:
    """回傳符合『證據等級至少跟 min_evidence_tier 一樣強』的內容，依相似度排序。"""
    required_rank = TIER_RANK[min_evidence_tier]

    query = db.query(ContentChunk)
    if product_id:
        query = query.filter(ContentChunk.product_id == product_id)
    all_chunks = query.all()

    # 先過濾證據等級：只留下等級「跟要求一樣強或更強」的內容
    eligible = [c for c in all_chunks if TIER_RANK.get(c.evidence_tier, 99) <= required_rank]
    if not eligible:
        return []

    corpus = [c.text for c in eligible] + [question]
    # 中文沒有空白分詞，sklearn 預設的 word-boundary 斷詞方式對中文完全失效
    # （會抓不到任何相似度）。改用字元 n-gram（analyzer="char_wb"）
    # 是不需要額外裝中文斷詞套件（如 jieba）也能work的做法。
    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
    matrix = vectorizer.fit_transform(corpus)
    question_vec = matrix[-1]
    doc_vecs = matrix[:-1]
    scores = cosine_similarity(question_vec, doc_vecs)[0]

    ranked = sorted(zip(eligible, scores), key=lambda x: x[1], reverse=True)
    results = [
        RetrievedChunk(
            id=c.id,
            text=c.text,
            evidence_tier=c.evidence_tier,
            claim_type=c.claim_type,
            source_citation=c.source_citation,
            score=float(score),
        )
        for c, score in ranked[:top_k]
        if score > 0
    ]
    return results
