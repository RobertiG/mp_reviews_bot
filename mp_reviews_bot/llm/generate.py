from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class LLMResponse:
    text: str
    confidence: int
    conflict: bool


def generate_response(event: Dict[str, Any], kb_rules: List[Dict[str, Any]]) -> LLMResponse:
    texts = {rule.get("text") for rule in kb_rules}
    conflict = len(texts) > 1
    confidence = 30 if conflict else 80
    reply_text = f"Ответ на: {event.get('text', '')}" or ""
    return LLMResponse(text=reply_text, confidence=confidence, conflict=conflict)
