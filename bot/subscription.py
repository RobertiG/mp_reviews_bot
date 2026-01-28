from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request


def get_chat_member(bot_token: str, chat_id: str, user_id: int) -> str:
    """Return chat member status from Telegram API.

    Raises RuntimeError when API request fails or returns error.
    """
    if not bot_token:
        raise RuntimeError("Bot token is not configured")
    url = f"https://api.telegram.org/bot{bot_token}/getChatMember"
    payload = urllib.parse.urlencode({"chat_id": chat_id, "user_id": user_id}).encode(
        "utf-8"
    )
    try:
        with urllib.request.urlopen(url, data=payload, timeout=10) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise RuntimeError("Failed to contact Telegram API") from exc

    data = json.loads(raw)
    if not data.get("ok"):
        raise RuntimeError(data.get("description", "Telegram API error"))
    result = data.get("result", {})
    return result.get("status", "left")


def is_subscribed(status: str) -> bool:
    return status in {"member", "administrator", "creator"}
