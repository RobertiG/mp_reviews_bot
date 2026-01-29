from app.integrations.marketplace import MarketplaceClient


class OzonClient(MarketplaceClient):
    def fetch_events(self):
        return []

    def send_reply(self, marketplace_event_id: str, text: str) -> bool:
        return True
