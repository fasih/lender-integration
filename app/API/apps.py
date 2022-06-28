from django.apps import AppConfig


class APIConfig(AppConfig):
    name = 'API'
    verbose_name = 'API'

    def ready(self):
        from API.v1.tasks import shared_task
