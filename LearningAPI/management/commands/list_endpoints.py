from django.core.management.base import BaseCommand
from django.urls import resolve
from rest_framework.views import APIView

class Command(BaseCommand):
    help = "List all endpoints and their methods"

    def handle(self, *args, **options):
        urlresolver = resolve
        endpoints = []

        for url_pattern in urlresolver(None).url_patterns:
            if isinstance(url_pattern.callback, APIView):
                methods = [method.upper() for method in url_pattern.callback.http_method_names]
                endpoint = {
                    "path": url_pattern.pattern._route,
                    "methods": methods,
                }
                endpoints.append(endpoint)

        self.stdout.write("List of Endpoints:")
        for endpoint in endpoints:
            self.stdout.write(f"Path: {endpoint['path']}")
            self.stdout.write(f"Methods: {', '.join(endpoint['methods'])}\n")
