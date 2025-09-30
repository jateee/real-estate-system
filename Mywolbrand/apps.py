from django.apps import AppConfig

class MywolbrandConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Mywolbrand"

    def ready(self):
        import Mywolbrand.signals




