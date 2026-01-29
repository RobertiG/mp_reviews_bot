def should_autosend(confidence: int, has_conflict: bool, min_confidence: int = 50) -> bool:
    if has_conflict:
        return False
    return confidence >= min_confidence
