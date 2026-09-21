"""意圖分類：MVP 先用關鍵字規則，之後量大了可以換成分類模型或 LLM 結構化輸出。"""

MEDICAL_CLAIM_KEYWORDS = ["治療", "治癒", "根治", "消除疤痕", "醫療", "療效", "副作用", "過敏"]
COMPLAINT_KEYWORDS = ["退貨", "退款", "壞掉", "瑕疵", "客訴", "投訴", "不滿意"]


def classify(question: str) -> str:
    if any(kw in question for kw in MEDICAL_CLAIM_KEYWORDS):
        return "MEDICAL_EFFICACY_CLAIM"
    if any(kw in question for kw in COMPLAINT_KEYWORDS):
        return "COMPLAINT"
    if question.strip():
        return "GENERAL_PRODUCT_INFO"
    return "UNKNOWN"
