from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, List, Optional


@dataclass(frozen=True)
class Button:
    text: str
    action: str
    url: Optional[str] = None


@dataclass(frozen=True)
class Screen:
    key: str
    title: str
    body: str
    buttons: List[List[Button]] = field(default_factory=list)
    keyboard: str = "inline"


@dataclass
class UserContext:
    user_id: int
    is_admin: bool = False
    has_subscription: Optional[bool] = None
    current_project_id: Optional[int] = None
    current_project_name: Optional[str] = None
    projects: List[dict] = field(default_factory=list)
    dashboard: Optional[dict] = None
    feed: List[dict] = field(default_factory=list)
    feed_filters: Optional[dict] = None
    card: Optional[dict] = None
    edit_draft: Optional[str] = None
    kb_rule_draft: Optional[dict] = None
    kb_rules: List[dict] = field(default_factory=list)
    cabinets: List[dict] = field(default_factory=list)
    onboarding: Optional[dict] = None
    settings: Optional[dict] = None
    balance: Optional[dict] = None


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
