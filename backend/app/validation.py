"""事後驗證：模型答完之後，再檢查一次有沒有超線。

這一層存在的理由：就算前面的 prompt 限制得再嚴謹，模型還是有機率不聽話，
所以不能只靠「叫模型不要亂講」，要有一個獨立於模型之外、可以單獨測試的
檢查關卡。
"""
from dataclasses import dataclass
from typing import List

from app.decision_table import DecisionRule
from app.retrieval import RetrievedChunk


@dataclass
class ValidationResult:
    passed: bool
    reasons: List[str]


def validate(response: str, chunks_used: List[RetrievedChunk], rule: DecisionRule) -> ValidationResult:
    reasons = []

    # 1. 禁用詞檢查
    hit_banned = [w for w in rule.banned_words if w in response]
    if hit_banned:
        reasons.append(f"回答中出現禁用詞：{hit_banned}")

    # 2. 引用來源檢查（如果有用到內容，理論上回答應該至少與某個 chunk 有語意重疊，
    #    MVP 先用最簡單的規則：只要有檢索到內容，就要求回答不能是空的、
    #    且不能是「我不知道」這種完全沒有根據內容作答的空話）
    if chunks_used and len(response.strip()) < 5:
        reasons.append("回答內容過短，可能沒有根據檢索到的內容作答")

    return ValidationResult(passed=len(reasons) == 0, reasons=reasons)
