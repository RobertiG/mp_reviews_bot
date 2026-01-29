import os

ACTION_START = "start"
ACTION_SELECT_PROJECT = "select_project"
ACTION_DASHBOARD = "dashboard"
ACTION_FEED = "feed"
ACTION_FEED_FILTERS = "feed_filters"
ACTION_CARD = "card"
ACTION_EDIT = "edit"
ACTION_REGENERATE = "regenerate"
ACTION_KB_LIST = "kb_list"
ACTION_KB_DELETE = "kb_delete"
ACTION_CABINETS = "cabinets"
ACTION_ONBOARDING = "onboarding"
ACTION_PROJECT_SETTINGS = "project_settings"
ACTION_BALANCE = "balance"
ACTION_CHECK_SUBSCRIPTION = "sub_check"
ACTION_ADD_KB_RULE = "add_kb_rule"
ACTION_SUBSCRIPTION = "subscription"
ACTION_BACK = "back"

DEFAULT_REQUIRED_CHANNEL = os.getenv("BOT_REQUIRED_CHANNEL", "@mp_reviews_channel")
DEFAULT_BOT_TOKEN = os.getenv("BOT_TOKEN", "")
