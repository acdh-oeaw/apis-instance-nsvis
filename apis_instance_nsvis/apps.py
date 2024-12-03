from django.apps import AppConfig


class ApisInstanceNsvisConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "apis_instance_nsvis"

    def ready(self):
        import apis_instance_nsvis.signals
