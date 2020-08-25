from django.apps import AppConfig


class TradingappConfig(AppConfig):
    name = 'tradingapp'

    def ready(self) -> None:
        import profiles.signals  # noqa: E261 F401
        super().ready()
