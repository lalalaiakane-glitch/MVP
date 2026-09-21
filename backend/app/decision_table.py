"""讀取 decision_table.yaml，提供意圖 -> 規則的查詢。"""
from dataclasses import dataclass
from pathlib import Path
from typing import List
import yaml

_YAML_PATH = Path(__file__).parent / "decision_table.yaml"


@dataclass
class DecisionRule:
    intent: str
    description: str
    min_evidence_tier: str
    allowed_tone: str
    fallback_action: str  # REFER_HUMAN / CONSERVATIVE_ANSWER
    banned_words: List[str]
    always_fallback: bool = False  # True 代表這類意圖一律不讓 LLM 回答，不管有沒有檢索到內容


def _load_table() -> dict:
    with open(_YAML_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


_TABLE = _load_table()


def lookup(intent: str) -> DecisionRule:
    """查詢某個意圖對應的規則；查不到就退回 UNKNOWN（最保守）。"""
    entry = _TABLE.get(intent) or _TABLE["UNKNOWN"]
    return DecisionRule(
        intent=intent if intent in _TABLE else "UNKNOWN",
        description=entry["description"],
        min_evidence_tier=entry["min_evidence_tier"],
        allowed_tone=entry["allowed_tone"],
        fallback_action=entry["fallback_action"],
        banned_words=entry.get("banned_words", []),
        always_fallback=entry.get("always_fallback", False),
    )


def reload_table():
    """讓 API 可以在改完 YAML 後不用重啟服務就重新載入（方便你邊調邊測）。"""
    global _TABLE
    _TABLE = _load_table()
