from app.schemas import LLMResponse


class LLMAdapter:
    def generate(self, prompt: str) -> LLMResponse:
        return LLMResponse(text="", confidence=0, kb_rule_ids=[], conflict=False)
