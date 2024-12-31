from django.db import models


class RequestQuery(models.Model):
    query = models.TextField(null=False, blank=False)
    searcher = models.ForeignKey('NSSUser', on_delete=models.CASCADE, related_name='search_queries')
    helpful_request = models.ForeignKey('HelpRequest', on_delete=models.SET_NULL, null=True, blank=True)
