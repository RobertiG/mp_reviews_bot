from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, List, Optional


@dataclass(frozen=True)
class Button:
    text: str
    action: str


@dataclass(frozen=True)
class Screen:
    key: str
    title: str
    body: str
    buttons: List[List[Button]] = field(default_factory=list)
    keyboard: str = "reply"


@dataclass
class UserContext:
    user_id: int
    is_admin: bool = False
    has_subscription: Optional[bool] = None
    current_project: Optional[str] = None
    projects: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class BotDependencies:
    bot_token: str
    required_channel: str
    get_chat_member: Callable[[str, str, int], str]


@dataclass(frozen=True)
class NavigationResult:
    screen: Screen
    notices: List[str] = field(default_factory=list)


Keyboard = Iterable[Iterable[Button]]
