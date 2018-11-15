from django.apps import AppConfig


class ClaimsAppConfig(AppConfig):

    name = "ocr_receipt_scanner.claims"
    verbose_name = "Claims"

    def ready(self):
        try:
            import claims.signals  # noqa F401
        except ImportError:
            pass