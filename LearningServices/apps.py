from django.apps import AppConfig


class LearningservicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "LearningServices"

    def ready(self):
        import LearningServices.signals
