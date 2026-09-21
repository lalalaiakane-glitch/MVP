"""串起 intent -> decision_table -> retrieval -> prompt -> llm -> validation，
回傳完整 trace，讓前端可以把整個「黑箱」攤開來看。
"""
from dataclasses import dataclass, asdict
from typing import List, Optional

from sqlalchemy.orm import Session

from app import intent, decision_table, retrieval, validation
from app.llm_client import get_llm_client


@dataclass
class PipelineResult:
    question: str
    detected_intent: str
    rule_description: str
    min_evidence_tier_required: str
    retrieved_chunks: List[dict]
    fallback_triggered: bool
    fallback_action: Optional[str]
    prompt_used: Optional[str]
    raw_response: Optional[str]
    final_response: str
    validation_passed: Optional[bool]
    validation_reasons: List[str]


FALLBACK_MESSAGES = {
    "REFER_HUMAN": "這個問題涉及需要專業判斷的內容，已為您轉接真人客服，稍後會有專人與您聯繫。",
    "CONSERVATIVE_ANSWER": "目前沒有足夠資料能明確回答這個問題，建議您參考產品官方說明，或聯繫客服進一步確認。",
}


def run(db: Session, question: str, product_id: Optional[str] = None) -> PipelineResult:
    # Step 1：意圖分類
    detected_intent = intent.classify(question)

    # Step 2：查決策表
    rule = decision_table.lookup(detected_intent)

    # Step 2.5：某些意圖（例如客訴）一律不讓 LLM 接手，不管檢索結果如何
    if rule.always_fallback:
        return PipelineResult(
            question=question,
            detected_intent=rule.intent,
            rule_description=rule.description,
            min_evidence_tier_required=rule.min_evidence_tier,
            retrieved_chunks=[],
            fallback_triggered=True,
            fallback_action=rule.fallback_action,
            prompt_used=None,
            raw_response=None,
            final_response=FALLBACK_MESSAGES.get(rule.fallback_action, "無法回答此問題。"),
            validation_passed=None,
            validation_reasons=[f"意圖為 {rule.intent}，規則設定一律轉真人/固定回應，不呼叫模型"],
        )

    # Step 3：依證據等級過濾檢索
    chunks = retrieval.search(
        db, question, min_evidence_tier=rule.min_evidence_tier, product_id=product_id
    )

    # Step 4：檢索不到足夠等級的證據 -> 直接走 fallback，不呼叫模型
    if not chunks:
        return PipelineResult(
            question=question,
            detected_intent=rule.intent,
            rule_description=rule.description,
            min_evidence_tier_required=rule.min_evidence_tier,
            retrieved_chunks=[],
            fallback_triggered=True,
            fallback_action=rule.fallback_action,
            prompt_used=None,
            raw_response=None,
            final_response=FALLBACK_MESSAGES.get(rule.fallback_action, "無法回答此問題。"),
            validation_passed=None,
            validation_reasons=["找不到符合最低證據等級要求的內容，未呼叫模型"],
        )

    # Step 5：組 prompt、呼叫模型
    context_block = "\n".join(
        f"- ({c.evidence_tier}級證據) {c.text}（來源：{c.source_citation or '未標註'}）"
        for c in chunks
    )
    prompt = f"""你是品牌客服助理。只能根據以下內容回答，不能加入未列出的資訊。
語氣限制：{rule.allowed_tone}

可用內容：
{context_block}

使用者問題：{question}
"""
    llm = get_llm_client()
    raw_response = llm.generate(prompt)

    # Step 6：事後驗證
    result = validation.validate(raw_response, chunks, rule)

    final_response = raw_response
    if not result.passed:
        # 驗證沒過，不把可能超線的回答直接送出去，改走 fallback
        final_response = FALLBACK_MESSAGES.get(rule.fallback_action, "此問題需要人工協助確認。")

    return PipelineResult(
        question=question,
        detected_intent=rule.intent,
        rule_description=rule.description,
        min_evidence_tier_required=rule.min_evidence_tier,
        retrieved_chunks=[asdict(c) for c in chunks],
        fallback_triggered=False,
        fallback_action=None,
        prompt_used=prompt,
        raw_response=raw_response,
        final_response=final_response,
        validation_passed=result.passed,
        validation_reasons=result.reasons,
    )
