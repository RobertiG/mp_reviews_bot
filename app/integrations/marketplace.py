from typing import Protocol, List


class MarketplaceEvent(dict):
    pass


class MarketplaceClient(Protocol):
    def fetch_events(self) -> List[MarketplaceEvent]:
        ...

    def send_reply(self, marketplace_event_id: str, text: str) -> bool:
        ...
