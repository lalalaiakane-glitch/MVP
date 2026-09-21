"""LLM 呼叫層，做成介面方便抽換。

預設用 MockLLMClient：不用任何金鑰，回傳固定格式的回答，方便你在還沒申請
任何 API Key 之前，先把整條 pipeline（意圖->檢索->決策->驗證）跑通。

真的要接模型時，設定環境變數 GEMINI_API_KEY（用前面聊過的 Google AI Studio
免卡免費額度），會自動切換成 GeminiLLMClient。
"""
import os
from abc import ABC, abstractmethod

import httpx


class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        ...


class MockLLMClient(LLMClient):
    """假的模型，方便沒有金鑰時測試整條流程。"""

    def generate(self, prompt: str) -> str:
        return (
            "[MOCK 回答，未呼叫真實模型] 根據提供的內容，"
            "以下是基於檢索結果的保守摘要回答。"
            "（設定 GEMINI_API_KEY 環境變數後會改成呼叫真實模型）"
        )


class GeminiLLMClient(LLMClient):
    """用 Google AI Studio 的 Gemini API（免卡免費額度）。"""

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str) -> str:
        url = (
            f"https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            resp = httpx.post(url, json=payload, timeout=30.0)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:  # noqa: BLE001 - MVP 階段先簡單處理，記錄下來即可
            return f"[LLM 呼叫失敗：{e}]"


def get_llm_client() -> LLMClient:
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return GeminiLLMClient(api_key=api_key)
    return MockLLMClient()
