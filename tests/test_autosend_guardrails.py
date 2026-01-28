from mp_reviews_bot.autosend import guardrails


def test_autosend_blocked_on_conflict_or_low_confidence():
    assert guardrails.should_autosend(confidence=85, has_conflict=True) is False
    assert guardrails.should_autosend(confidence=40, has_conflict=False) is False
    assert guardrails.should_autosend(confidence=90, has_conflict=False) is True


def test_autosend_requires_min_confidence_setting():
    assert (
        guardrails.should_autosend(
            confidence=70,
            has_conflict=False,
            min_confidence=80,
        )
        is False
    )
    assert (
        guardrails.should_autosend(
            confidence=85,
            has_conflict=False,
            min_confidence=80,
        )
        is True
    )
