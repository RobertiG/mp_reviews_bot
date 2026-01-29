from __future__ import annotations

from dataclasses import replace
from typing import Callable, Dict, List

from . import constants, screens
from .subscription import is_subscribed
from .types import BotDependencies, NavigationResult, Screen, UserContext


RouteHandler = Callable[[UserContext], Screen]


ADMIN_ACTIONS = {
    constants.ACTION_CABINETS,
    constants.ACTION_ONBOARDING,
    constants.ACTION_PROJECT_SETTINGS,
    constants.ACTION_BALANCE,
    constants.ACTION_KB_DELETE,
}


def _build_routes() -> Dict[str, RouteHandler]:
    return {
        constants.ACTION_START: lambda ctx: screens.start_screen(
            has_projects=bool(ctx.projects)
        ),
        constants.ACTION_SELECT_PROJECT: lambda ctx: screens.project_selection_screen(
            ctx.projects, ctx.is_admin
        ),
        constants.ACTION_DASHBOARD: lambda ctx: screens.dashboard_screen(
            ctx.current_project_name, ctx.is_admin, ctx.dashboard
        ),
        constants.ACTION_FEED: lambda ctx: screens.feed_screen(ctx.feed, ctx.feed_filters),
        constants.ACTION_FEED_FILTERS: lambda ctx: screens.feed_filters_screen(ctx.feed_filters),
        constants.ACTION_CARD: lambda ctx: screens.card_screen(ctx.card),
        constants.ACTION_EDIT: lambda ctx: screens.edit_screen(ctx.edit_draft or (ctx.card or {}).get("suggested_reply")),
        constants.ACTION_REGENERATE: lambda ctx: screens.regenerate_screen(),
        constants.ACTION_ADD_KB_RULE: lambda ctx: screens.add_kb_rule_screen(ctx.kb_rule_draft),
        constants.ACTION_KB_LIST: lambda ctx: screens.kb_list_screen(ctx.is_admin, ctx.kb_rules),
        constants.ACTION_KB_DELETE: lambda ctx: screens.kb_delete_screen(ctx.kb_rules),
        constants.ACTION_CABINETS: lambda ctx: screens.cabinets_screen(ctx.cabinets),
        constants.ACTION_ONBOARDING: lambda ctx: screens.onboarding_screen(ctx.onboarding),
        constants.ACTION_PROJECT_SETTINGS: lambda ctx: screens.project_settings_screen(ctx.settings),
        constants.ACTION_BALANCE: lambda ctx: screens.balance_screen(ctx.balance),
    }


def _resolve_subscription(
    ctx: UserContext,
    deps: BotDependencies,
    checker: Callable[[str], bool] = is_subscribed,
) -> UserContext:
    status = deps.get_chat_member(deps.bot_token, deps.required_channel, ctx.user_id)
    return replace(ctx, has_subscription=checker(status))


def handle_action(
    action: str,
    ctx: UserContext,
    deps: BotDependencies,
) -> NavigationResult:
    notices: List[str] = []
    if deps.required_channel:
        if action == constants.ACTION_CHECK_SUBSCRIPTION or ctx.has_subscription is None:
            try:
                ctx = _resolve_subscription(ctx, deps)
            except RuntimeError as exc:
                notices.append(str(exc))
                return NavigationResult(
                    screen=screens.subscription_required(deps.required_channel, None),
                    notices=notices,
                )
        if not ctx.has_subscription:
            return NavigationResult(
                screen=screens.subscription_required(deps.required_channel, None),
                notices=notices,
            )

    if action in ADMIN_ACTIONS and not ctx.is_admin:
        notices.append("Недостаточно прав для этого раздела.")
        return NavigationResult(
            screen=screens.dashboard_screen(ctx.current_project, ctx.is_admin),
            notices=notices,
        )

    routes = _build_routes()
    handler = routes.get(action, routes[constants.ACTION_START])
    return NavigationResult(screen=handler(ctx), notices=notices)
