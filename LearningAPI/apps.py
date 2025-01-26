from django.apps import AppConfig

class LearningAPIConfig(AppConfig):
    name = 'LearningAPI'

    def ready(self):
        # Import the signals module to ensure signal handlers are connected
        # import LearningAPI.signals
        pass
